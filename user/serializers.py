from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core import exceptions
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from location.serializers import NationalitySerializer
from user.models import User, UserProfile


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    def validate(self, data):
        user = getattr(self, "user", None) or self.context["request"].user
        if not user.check_password(data["current_password"]):
            raise serializers.ValidationError({"password": _("Current password is incorrect.")})
        return super().validate(data)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    def validate(self, data):
        user = getattr(self, "user", None) or self.context["request"].user

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": _("Password fields did not match.")})

        try:
            validate_password(data["new_password"], user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return super().validate(data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "username", "email", "created_date", "slug")
        read_only_fields = [
            "email",
            "slug",
        ]


class User2FA(serializers.ModelSerializer):
    backup_tokens = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("primary_verification_method", "email_verification_enabled", "otp_enabled", "otp_auth_url",
                  "backup_enabled", "backup_tokens")

    def to_representation(self, instance):
        data = super().to_representation(instance)

        tokens = instance.backup_tokens
        if tokens:
            tokens_split = tokens.split("|")
            data["backup_tokens"] = tokens_split
        return data


class Token(serializers.Serializer):
    token = serializers.CharField(required=True)


class TwoFactorMethods(CurrentPasswordSerializer):
    TYPE_CHOICES = (("OTP", _("One-Time Password")), ("EMAIL", _("Email")))
    type = serializers.ChoiceField(choices=TYPE_CHOICES, required=True)

    def validate(self, data):
        user = self.context["request"].user
        if data.get("type") == "OTP" and not user.otp_enabled:
            raise serializers.ValidationError(_("OTP is not activated."))
        elif data.get("type") == "EMAIL" and not user.email_verification_enabled:
            raise serializers.ValidationError(_("Email verification is not activated."))
        return super().validate(data)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True, required=True)
    confirm_password = serializers.CharField(style={"input_type": "password"}, write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "username", "email", "password", "confirm_password")

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        try:
            validate_password(attrs["password"], self.instance)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserDeletionSerializer(CurrentPasswordSerializer):
    pass


class ResendAccountActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def get_user(self, is_active=False):
        email = self.validated_data["email"]
        try:
            user = User.objects.get(email=email, is_active=is_active)
            return user
        except User.DoesNotExist:
            return None


class PasswordChangeSerializer(CurrentPasswordSerializer, PasswordSerializer):

    def validate(self, data):
        data = super().validate(data)
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError(
                {"password": _("Password cannot be the same as the old password.")})
        return data


class EmailChangeSerializer(CurrentPasswordSerializer):
    new_email = serializers.EmailField()

    class Meta:
        Model = User
        fields = "__all__"

    def validate(self, data):
        user = self.context["request"].user
        new_email = data.get("new_email")

        existing_user_with_email = User.objects.filter(email=new_email).exclude(pk=user.pk).first()
        if existing_user_with_email:
            raise serializers.ValidationError({"email": _("Email is already associated with another account.")},
                                              code="invalid")

        if new_email == user.email:
            raise serializers.ValidationError({"email": _("Email matches your current email.")}, code="invalid")

        unverified_user_with_email = User.objects.filter(new_email=new_email).exclude(pk=user.pk).first()
        if unverified_user_with_email:
            raise serializers.ValidationError(
                {"email": _("Email is already in use for an unverified email change request.")}, code="invalid")

        return super().validate(data)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(PasswordSerializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data["uidb64"]).decode()
            self.user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            raise serializers.ValidationError({"token", _("Invalid token or user not found.")})

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError({"token", _("Invalid token.")})
        return super().validate(data)


class UserProfileSerializer(serializers.ModelSerializer):
    profile_url = serializers.HyperlinkedIdentityField(view_name="user-profile-detail")
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    age = serializers.IntegerField(read_only=True)
    avg_rating_and_reviews_as_freelancer = serializers.SerializerMethodField()
    avg_rating_and_reviews_as_client = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        exclude = ("user", "modified_date")

    @staticmethod
    def get_avg_rating_and_reviews_as_freelancer(obj):
        return obj.avg_rating_and_reviews_as_freelancer

    @staticmethod
    def get_avg_rating_and_reviews_as_client(obj):
        return obj.avg_rating_and_reviews_as_client

    def to_representation(self, instance):
        data = super().to_representation(instance)
        nationality_data = NationalitySerializer(instance.nationality.all(), many=True).data
        if nationality_data:
            data["nationality"] = [item["nationality"] for item in nationality_data]
        else:
            data["nationality"] = None
        location = instance.location
        if location:
            location_data = {
                "city": location.city,
                "country": location.country,
            }
            data["location"] = location_data
        else:
            data["location"] = None
        return data

    # def get_portfolio(self, i):
    #     x = UserPreviousWork.objects.filter(user__username=i.user.username)
    #     serializer = z(x, many=True, context={"request": self.context["request"]})
    #     return serializer.data
