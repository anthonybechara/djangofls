from urllib.parse import quote

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Avg, Count
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from education.models import University, Degree, Major, Skill
from location.models import Location, Nationality
from payment.models import Bid, Point
from user_resume.models import UserReview, UserStatistics


class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None,
                    **extra_fields):
        if not first_name:
            raise ValueError(_("The First name field must be set"))
        if not last_name:
            raise ValueError(_("The Last name field must be set"))
        if not username:
            raise ValueError(_("The Username field must be set"))
        if not email:
            raise ValueError(_("The Email field must be set"))

        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, username, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_admin") is not True:
            raise ValueError(_("Superuser must have is_admin = True."))

        email = self.normalize_email(email)
        return self.create_user(first_name, last_name, username, email, password, **extra_fields)


username_validator = RegexValidator(regex=r'^[\w.@]+$',
                                    message=_(
                                        "Enter a valid username. This value may contain only letters, numbers, and (@ _ .) characters."))

name_validator = RegexValidator(regex=r"^[a-zA-Z'\'\- ]+$",
                                message=_(
                                    "Enter a valid name. This value may contain only letters and score (-)."))


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True, validators=[username_validator],
                                verbose_name=_("Username"))
    email = models.EmailField(max_length=100, unique=True, verbose_name=_("Email"))
    new_email = models.EmailField(max_length=100, unique=True, verbose_name=_("New Email"), blank=True, null=True)
    new_email_modified = models.DateTimeField(blank=True, null=True, verbose_name=_("New Email Verification"))
    first_name = models.CharField(max_length=30, validators=[name_validator], verbose_name=_("First name"))
    last_name = models.CharField(max_length=30, validators=[name_validator], verbose_name=_("Last name"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Created Date"))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date"))
    is_active = models.BooleanField(default=False, verbose_name=_("Active"))
    is_admin = models.BooleanField(default=False, verbose_name=_("Admin"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    is_online = models.BooleanField(default=False, verbose_name=_("Online"))
    last_logout = models.DateTimeField(auto_now=True, verbose_name=_("Last Logout"))

    VERIFICATION_CHOICES = [
        ("EMAIL", _("Email")),
        ("OTP", _("One-Time Password")),
    ]

    primary_verification_method = models.CharField(
        max_length=10, choices=VERIFICATION_CHOICES, blank=True, null=True, verbose_name=_("Verification Method"))
    email_verification_enabled = models.BooleanField(default=False, verbose_name=_("2fa Email Status"))
    email_base32 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Email Base32"))
    otp_enabled = models.BooleanField(default=False, verbose_name=_("2fa OTP Status"))
    otp_base32 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("OTP Base32"))
    otp_auth_url = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("OTP Authentication URL"))
    backup_enabled = models.BooleanField(default=False, verbose_name=_("2fa Backup Status"))
    backup_tokens = models.TextField(blank=True, null=True, verbose_name=_("Backup Tokens"))

    def save(self, *args, **kwargs):
        if self.new_email:
            self.new_email_modified = timezone.now()
        if not self.slug:
            self.slug = slugify(self.username)
        super(User, self).save(*args, **kwargs)

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    def __str__(self):
        return self.username

    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
        setattr(self, self.USERNAME_FIELD, self.normalize_username(self.get_username()))

        if self.otp_enabled or self.email_verification_enabled:
            if not self.primary_verification_method:
                raise ValidationError(
                    _("Primary verification method must be set if OTP or email verification is enabled."))
        elif not self.otp_enabled and not self.email_verification_enabled:
            if self.primary_verification_method:
                raise ValidationError(
                    _("Primary verification method should be None if OTP and email verification are disabled."))

    @staticmethod
    def has_perm(perm, obj=None, **kwargs):
        return True

    @staticmethod
    def has_module_perms(app_label, **kwargs):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def get_short_name(self):
        return self.first_name


Gender = (
    ("male", _("Male")),
    ("female", _("Female"))
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def profile_picture_upload_path(self, filename):
        path = f"profile/{self.user.username}/pp/{filename}"
        path = path.replace("'", "_")
        path = quote(path)
        return path

    def cover_photo_upload_path(self, filename):
        path = f"profile/{self.user.username}/cp/{filename}"
        path = path.replace("'", "_")
        path = quote(path)
        return path

    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, default="pp.jpeg",
                                        verbose_name=_("Profile Picture"))
    cover_photo = models.ImageField(upload_to=cover_photo_upload_path, blank=True, null=True,
                                    verbose_name=_("Cover Photo"))
    bio = models.TextField(blank=True, null=True, verbose_name=_("Bio"))
    middle_name = models.CharField(max_length=30, blank=True, validators=[name_validator],
                                   verbose_name=_("Middle Name"))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_("Birth Date"))
    gender = models.CharField(choices=Gender, blank=True, max_length=10, verbose_name=_("Gender"))
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="user_locations", verbose_name=_("Location"))
    nationality = models.ManyToManyField(Nationality, blank=True, related_name="user_nationalities",
                                         verbose_name=_("Nationality"))
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date"))

    # slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    from user_resume.models import UserReview

    @property
    def age(self):
        today = timezone.now()
        if self.birth_date:
            age = today.year - self.birth_date.year - (
                    (today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        else:
            return None
        return age

    @property
    def avg_rating_and_reviews_as_freelancer(self):
        reviews_info = UserReview.objects.filter(
            reviewed_user=self.user,
            reviewed_user_title="freelancer"
        ).aggregate(avg_rating=Avg("rating"), num_reviews=Count("id"))

        avg_rating = reviews_info["avg_rating"] or 0
        num_reviews = reviews_info["num_reviews"] or 0

        return avg_rating, num_reviews

    @property
    def avg_rating_and_reviews_as_client(self):
        reviews_info = UserReview.objects.filter(
            reviewed_user=self.user,
            reviewed_user_title="client"
        ).aggregate(avg_rating=Avg("rating"), num_reviews=Count("id"))

        avg_rating = reviews_info["avg_rating"] or 0
        num_reviews = reviews_info["num_reviews"] or 0

        return avg_rating, num_reviews

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return str(_(f"{self.user.username}'s Profile"))


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserStatistics.objects.create(user=instance)
        Point.objects.create(user=instance)
        Bid.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
