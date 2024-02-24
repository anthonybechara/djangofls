from urllib.parse import quote

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from education.models import Skill

STATUS_CHOICES = (
    ("active", _("Active")),
    ("in_progress", _("In Progress")),
    ("completed", _("Completed")),
    ("canceled", _("Canceled")),
    ("expired", _("Expired")),
)


class Project(models.Model):
    published_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                       related_name="user_projects")
    published_username = models.CharField(max_length=200, blank=True, verbose_name=_("Published Username"))
    title = models.CharField(max_length=200, blank=False, validators=[
        RegexValidator(regex="^[A-Za-z0-9\s]*$", message=_("Only characters, numbers and spaces are allowed."),
                       code="invalid_title")], verbose_name=_("Project Title"))
    description = models.TextField(blank=False, verbose_name=_("Project description"))
    additional_notes = models.CharField(max_length=200, blank=True, verbose_name=_("Additional Notes"))
    skill_needed = models.ManyToManyField(Skill, related_name="project_needed")
    min_price = models.IntegerField(validators=[MinValueValidator(10)], blank=False, null=False,
                                    verbose_name=_("Minimum Price"))
    max_price = models.IntegerField(blank=False, null=False, verbose_name=_("Maximum Price"))
    due_date = models.DateField(blank=False, null=False, verbose_name=_("Due Date"))
    proposal_time_end = models.DateField(blank=False, null=False, verbose_name=_("Proposal Time End"))
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name=_("Project Status"))

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        if self.published_user:
            return str(_(f"{self.published_user}'s Project ({self.title})"))
        return str(_(f"{self.published_username} Project ({self.title})"))

    def clean(self):
        if self.min_price > self.max_price:
            raise ValidationError(_("Minimum price cannot be greater than maximum price."))
        # x = self.min_price * Decimal("0.3")
        # if not self.max_price >= round(x) + self.min_price:
        #     raise ValidationError(_(f"Maximum must be at least {self.min_price + round(x)}."))
        if self.due_date < timezone.now().date():
            raise ValidationError(_("Due date cannot be in the past."))
        if self.proposal_time_end > self.due_date:
            raise ValidationError({"proposal_time_end": _("Proposal time end must be before the due date.")})


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_files")

    def project_file_path(self, filename):
        path = f"project_files/{self.project.published_user}/{self.project.title}/{filename}"
        path = path.replace("'", "_")
        path = quote(path)
        return path

    file = models.FileField(upload_to=project_file_path, verbose_name=_("File"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))

    class Meta:
        verbose_name = _("Project File")
        verbose_name_plural = _("Project Files")


class ProjectProposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_proposals")
    proposer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                 related_name="user_proposals")
    proposer_username = models.CharField(max_length=200, blank=True, verbose_name=_("Proposer Username"))
    proposal_text = models.TextField(blank=False, verbose_name=_("Proposal Text"))
    proposed_price = models.IntegerField(validators=[MinValueValidator(10)],
                                         blank=False, null=False, verbose_name=_("Proposed Price"))
    submission_date = models.DateField(blank=False, null=False, verbose_name=_("Submission Date"))
    proposal_date = models.DateTimeField(auto_now_add=True)
    is_price_adjusted = models.BooleanField(default=False, verbose_name=_("Adjust Price"))
    is_date_adjusted = models.BooleanField(default=False, verbose_name=_("Adjust Date"))
    is_accepted = models.BooleanField(default=False, verbose_name=_("Accepted"))
    is_canceled = models.BooleanField(default=False, verbose_name=_("Canceled"))

    class Meta:
        unique_together = ["project", "proposer"]
        verbose_name = _("Project Proposal")
        verbose_name_plural = _("Project Proposals")

    def __str__(self):
        # if self.project and self.proposer:
        #     return str(_(f"{self.proposer_username}'s Proposal for {self.project.title}"))
        # elif self.proposer:
        #     return str(_(f"{self.proposer_username}'s Proposal for (No associated project)"))
        # elif self.project:
        #     return str(_(f"No associated proposer for {self.project.title}"))
        # return str(_("No associated project nor proposer"))
        if self.proposer:
            return str(_(f"{self.proposer}'s Proposal for {self.project.title}"))
        return str(_(f"{self.proposer_username} Proposal for {self.project.title}"))

    def clean(self):
        if not self.is_price_adjusted:
            if self.proposed_price < self.project.min_price or self.proposed_price > self.project.max_price:
                raise ValidationError(_("Proposed price must be within the project's price range."))
        else:
            if self.project.min_price <= self.proposed_price <= self.project.max_price:
                raise ValidationError(_("Adjusted price should be outside the project's price range."))

        if not self.is_date_adjusted:
            if self.submission_date > self.project.due_date:
                raise ValidationError(_("Submission date must be before the project due date."))
        else:
            if self.submission_date <= self.project.due_date:
                raise ValidationError(_("Adjusted date should be after the project due date."))

        if self.project.published_user == self.proposer:
            raise ValidationError(_("The proposer cannot be the owner of the project."))

        if self.submission_date < timezone.now().date():
            raise ValidationError(_("Submission date cannot be in the past."))


class ChosenProposal(models.Model):
    project = models.OneToOneField(Project, on_delete=models.SET_NULL, null=True)
    selected_proposal = models.ForeignKey(ProjectProposal, on_delete=models.SET_NULL, null=True,
                                          related_name="selected_projects")
    chosen_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Chosen Date"))
    is_canceled = models.BooleanField(default=False, verbose_name=_("Canceled"))

    def __str__(self):
        return str(_(f"Chosen Proposal: {self.selected_proposal}"))

    class Meta:
        unique_together = ["project", "selected_proposal"]
        verbose_name = _("Chosen Proposal")
        verbose_name_plural = _("Chosen Proposals")

    def clean(self):
        if self.project != self.selected_proposal.project:
            raise ValidationError(_("The selected proposal must belong to the same project."))


class Dispute(models.Model):
    proposal = models.ForeignKey(ChosenProposal, on_delete=models.CASCADE, related_name="disputes")
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  related_name="user_disputes", verbose_name=_("Opened By"))
    opened_by_username = models.CharField(max_length=200, blank=True, verbose_name=_("Opened By Username"))
    description = models.TextField(blank=False, verbose_name=_("Dispute Description"))
    opened_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Opened At"))
    is_resolved = models.BooleanField(default=False, verbose_name=_("Resolved"))

    class Meta:
        unique_together = ["proposal", "opened_by"]
        verbose_name = _("Dispute")
        verbose_name_plural = _("Disputes")

    def __str__(self):
        if self.opened_by:
            return str(_(f"Dispute opened by {self.opened_by} on {self.proposal.project} project"))
        return str(_(f"Dispute opened by {self.opened_by_username} on {self.proposal.project} project"))

    def clean(self):
        if self.opened_by != self.proposal.project.published_user and self.opened_by != self.proposal.selected_proposal.proposer:
            raise ValidationError(_("The disputant must be either the project owner or the selected proposer."))
