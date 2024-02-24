from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from education.models import University, Degree, Major, Skill
from project.models import Project, ChosenProposal, ProjectProposal


class UserEducation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_educations")
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="user_universities",
                                   verbose_name=_("University"))
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name="user_degrees", verbose_name=_("Degree"))
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="user_majors", verbose_name=_("Major"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))

    class Meta:
        verbose_name = _("User Education")
        verbose_name_plural = _("User Educations")
        ordering = ["-start_date"]

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"date error", _("End date must be after the start date.")})

    def __str__(self):
        return str(_(f"{self.user}'s Education"))


class UserSkill(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill, related_name="user_skills", verbose_name=_("Skills"))

    class Meta:
        verbose_name = _("User Skill")
        verbose_name_plural = _("User Skills")

    def __str__(self):
        return str(_(f"User: {self.user}"))


class UserPortfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_portfolio")
    WORK_TYPE_CHOICES = (
        ("image", _("Image")),
        ("video", _("Video")),
        ("audio", _("Audio")),
        ("code", _("Code")),
        ("article", _("Article")),
        ("others", _("Others")),
    )
    work_type = models.CharField(max_length=40, choices=WORK_TYPE_CHOICES)
    title = models.CharField(max_length=100, blank=False, verbose_name=_("Work Title"))
    description = models.TextField(blank=False, verbose_name=_("Work Description"))
    sample = models.TextField(blank=True, verbose_name=_("Work Sample"))
    skills = models.ManyToManyField(Skill, related_name="work_skills")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = _("User Portfolio")
        verbose_name_plural = _("User Portfolios")

    def __str__(self):
        return str(_(f"{self.get_work_type_display()}--{self.title} / {self.user}"))


class PortfolioFile(models.Model):
    portfolio_work = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE, related_name="portfolio_file")

    def portfolio_file_upload_path(self, filename):
        path = f"profile/{self.portfolio_work.user}/pw/{self.portfolio_work.title}/{filename}"
        path = path.replace("'", "_")
        path = quote(path)
        return path

    file = models.FileField(upload_to=portfolio_file_upload_path, verbose_name=_("File"))

    class Meta:
        verbose_name = _("Portfolio File")
        verbose_name_plural = _("Portfolio Files")

    def __str__(self):
        return str(_(f"File {self.id}"))


class UserExperience(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_experience")
    title = models.CharField(max_length=100, blank=False, verbose_name=_("Title"))
    company_name = models.CharField(max_length=100, verbose_name=_("Company Name"))
    position = models.CharField(max_length=100, verbose_name=_("Position"))
    description = models.TextField(verbose_name=_("Description"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))
    present = models.BooleanField(default=False, verbose_name=_("I am currently working in this position"))

    class Meta:
        verbose_name = _("User Work Experience")
        verbose_name_plural = _("User Work Experiences")
        ordering = ["-start_date"]

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"date error", _("End date must be after the start date.")})

    def __str__(self):
        return str(_(f"{self.position} at {self.company_name} ({self.start_date} - {self.end_date or _('Present')})"))


class UserSavedProject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_saved")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    saved_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Saved At"))

    class Meta:
        verbose_name = _("User Project Saved")
        verbose_name_plural = _("User Projects saved")
        ordering = ["-saved_time"]
        unique_together = ("user", "project")

    def __str__(self):
        return str(f"{self.user} - {self.project}")

    def clean(self):
        if self.user == self.project.published_user:
            raise ValidationError("You cannot save your own project.")


class UserReview(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name="project_reviews", null=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="reviews_given",
                                 verbose_name=_("Reviewer"), null=True)
    reviewed_user_title = models.CharField(max_length=30, choices=(("client", _("Client")),
                                                                   ("freelancer", _("Freelancer"))))
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                      related_name="reviews_received",
                                      verbose_name=_("Reviewed User"), null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True,
                                 verbose_name=_("Rating"))
    feedback = models.TextField(blank=True, null=True, verbose_name=_("Feedback"))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("User Review")
        verbose_name_plural = _("User Reviews")
        ordering = ["-created_at"]

    def clean(self):
        existing_reviews = UserReview.objects.filter(project=self.project, reviewer=self.reviewer).exclude(pk=self.pk)
        if existing_reviews.exists():
            raise ValidationError("You have already reviewed this project.")

        project_owner = self.project.published_user
        selected_proposal_proposer = None

        if hasattr(self.project, "chosenproposal"):
            selected_proposal_proposer = self.project.chosenproposal.selected_proposal.proposer

        reviewer_valid = self.reviewer in [project_owner, selected_proposal_proposer]
        reviewed_user_valid = self.reviewed_user in [project_owner, selected_proposal_proposer]

        if not hasattr(self.project, "chosenproposal"):
            raise ValidationError("A chosen proposal is required for reviews to be performed.")

        if not self.project.status == "completed":
            raise ValidationError("Reviews can only be performed for completed projects.")

        if self.reviewer == self.reviewed_user or not (reviewer_valid and reviewed_user_valid):
            raise ValidationError(
                "Only the project owner and the proposer of the selected proposal can perform reviews.")

        if self.project.published_user == self.reviewed_user and not self.reviewed_user_title == "client":
            raise ValidationError("The reviewed user must be the client.")

        elif self.project.published_user == self.reviewer and not self.reviewed_user_title == "freelancer":
            raise ValidationError("The reviewed user must be the freelancer.")

    def __str__(self):
        return str(_(f"Review by {self.reviewer} for {self.reviewed_user}"))


class UserStatistics(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_statistic")

    @property
    def total_earning(self):
        return \
                ChosenProposal.objects.filter(selected_proposal__proposer=self.user,
                                              project__status="completed").aggregate(
                    total_earning=Sum("selected_proposal__proposed_price"))["total_earning"] or 0

    @property
    def total_proposal(self):
        return ProjectProposal.objects.filter(proposer=self.user).count()

    @property
    def projects_taken(self):
        return ChosenProposal.objects.filter(selected_proposal__proposer=self.user).count()

    @property
    def projects_taken_completed(self):
        return ChosenProposal.objects.filter(selected_proposal__proposer=self.user, project__status="completed").count()

    @property
    def projects_made(self):
        return Project.objects.filter(published_user=self.user).count()

    @property
    def projects_made_completed(self):
        return Project.objects.filter(published_user=self.user, status="completed").count()

    @property
    def total_paid(self):
        return ChosenProposal.objects.filter(project__published_user=self.user, project__status="completed").aggregate(
            total_paid=Sum("selected_proposal__proposed_price"))["total_paid"] or 0

    class Meta:
        verbose_name = _("User Statistics")
        verbose_name_plural = _("User Statistics")

    def __str__(self):
        return str(_(f"{self.user}' statistics"))
