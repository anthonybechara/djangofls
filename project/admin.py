from django.contrib import admin

from project.models import Project, ProjectFile, ProjectProposal, ChosenProposal, Dispute


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "file", "uploaded_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id", "published_user", "published_username", "title", "min_price", "max_price", "due_date", "created",
        "status")
    filter_horizontal = ("skill_needed",)


@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = (
        "id", "proposer", "proposer_username", "project", "proposed_price", "submission_date", "proposal_date",
        "is_price_adjusted", "is_date_adjusted", "is_accepted", "is_canceled")


@admin.register(ChosenProposal)
class ChosenProposalAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "selected_proposal", "chosen_date", "is_canceled")


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("id", "proposal", "opened_by", "opened_by_username", "description", "opened_at", "is_resolved")
