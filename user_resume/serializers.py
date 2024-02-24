from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.reverse import reverse

from education.serializers import SkillSerializer
from user_resume.models import UserEducation, UserSkill, UserReview, UserPortfolio, PortfolioFile, UserExperience, \
    UserStatistics, UserSavedProject


class UserEducationSerializer(serializers.ModelSerializer):
    education_url = serializers.HyperlinkedIdentityField(view_name="user-educations-detail")
    user = serializers.StringRelatedField()

    class Meta:
        model = UserEducation
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["university"] = instance.university.name
        data["degree"] = instance.degree.name
        data["major"] = instance.major.name
        return data

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and start_date > timezone.now().date():
            raise serializers.ValidationError(_("Start date cannot be in the future."))

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(_("End date must be after the start date."))

        return data


class UserSkillSerializer(serializers.ModelSerializer):
    skills_url = serializers.HyperlinkedIdentityField(view_name="user-skills-detail")
    user = serializers.StringRelatedField()

    class Meta:
        model = UserSkill
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        skills_data = SkillSerializer(instance.skills.all(), many=True).data
        data["skills"] = []
        for item in skills_data:
            skill_info = item["name"]
            data["skills"].append(skill_info)
        return data


class PortfolioFileSerializer(serializers.ModelSerializer):
    file_url = serializers.HyperlinkedIdentityField(view_name="portfolio-file")

    class Meta:
        model = PortfolioFile
        fields = ("file_url", "file")


class UserPortfolioSerializer(serializers.ModelSerializer):
    portfolio_file = PortfolioFileSerializer(many=True, read_only=True)
    files = serializers.ListField(write_only=True, required=False, child=serializers.FileField())
    portfolio_url = serializers.HyperlinkedIdentityField(view_name="user-portfolio-detail")
    user = serializers.StringRelatedField()

    def validate(self, data):
        work_type = data.get("work_type")
        portfolio_file = data.get("files")
        sample = data.get("sample")

        if work_type in ["image", "video", "audio"]:
            if not portfolio_file:
                raise serializers.ValidationError(_("File is required for image, video, or audio type."))
            elif sample:
                raise serializers.ValidationError(_("Sample should not be provided for image, video, or audio type."))
        else:
            if not portfolio_file and not sample:
                raise serializers.ValidationError(_("Either file or sample is required for this work type."))

        return data

    def validate_skills(self, value):
        user = self.context["request"].user
        user_skills = UserSkill.objects.filter(user=user, skills__in=value)
        valid_skill_ids = user_skills.values_list("skills__id", flat=True)
        for skill in value:
            if skill.id not in valid_skill_ids:
                raise serializers.ValidationError(
                    _(f"Skill with ID {skill.id}s is not valid for the user."))
        return [skill.id for skill in value]

    class Meta:
        model = UserPortfolio
        fields = "__all__"

    def create(self, validated_data):
        files_data = validated_data.pop("files", [])
        skills_data = validated_data.pop("skills", [])
        portfolio_work = UserPortfolio.objects.create(**validated_data)
        portfolio_work.skills.set(skills_data)
        for file in files_data:
            PortfolioFile.objects.create(portfolio_work=portfolio_work, file=file)
        return portfolio_work

    def update(self, instance, validated_data):
        uploaded_files_data = validated_data.pop("files", [])
        for file in uploaded_files_data:
            PortfolioFile.objects.create(portfolio_work=instance, file=file)
        instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        skills_data = SkillSerializer(instance.skills.all(), many=True).data
        data["skills"] = []
        for item in skills_data:
            skill_info = item["name"]
            data["skills"].append(skill_info)
        return data


# class z(serializers.ModelSerializer):
#     class Meta:
#         model = UserPreviousWork
#         fields = ("id",)

class UserExperienceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = UserExperience
        fields = "__all__"

    def validate(self, data):
        present = data.get("present")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if present and end_date:
            raise serializers.ValidationError(
                {"error": _("You cannot be currently employed (present) and have an end date specified.")})
        elif not present and not end_date:
            raise serializers.ValidationError({"error": _(
                "Please provide either a current experience status (present) or an end date for the experience.")})

        if start_date and start_date > timezone.now().date():
            raise serializers.ValidationError(_("Start date cannot be in the future."))

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(_("End date must be after the start date."))

        return data


class UserSavedProjectSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField()
    project_url = serializers.SerializerMethodField()

    class Meta:
        model = UserSavedProject
        exclude = ("user",)

    def get_project_url(self, i):
        request = self.context.get("request")
        return reverse("projects-detail", kwargs={"pk": i.project.pk}, request=request)


class UserReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField()
    reviewed_user = serializers.StringRelatedField()

    class Meta:
        model = UserReview
        exclude = ("reviewed_user_title",)


class UserStatisticSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    total_proposal = serializers.IntegerField(read_only=True)
    projects_taken = serializers.IntegerField(read_only=True)
    projects_taken_completed = serializers.IntegerField(read_only=True)
    projects_made = serializers.IntegerField(read_only=True)
    projects_made_completed = serializers.IntegerField(read_only=True)
    total_earning = serializers.IntegerField(read_only=True)
    total_paid = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserStatistics
        fields = "__all__"
