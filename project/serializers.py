from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.reverse import reverse

from education.serializers import SkillSerializer
from payment.models import Bid, TransactionLog
from project.models import Project, ProjectFile, ProjectProposal, ChosenProposal, Dispute
from user_resume.models import UserReview, UserPortfolio, UserEducation, UserSkill, UserExperience


class ProjectFileSerializer(serializers.ModelSerializer):
    file_url = serializers.HyperlinkedIdentityField(view_name="proj-file-detail")

    class Meta:
        model = ProjectFile
        fields = ("file_url", "file")


class ProjectSerializer(serializers.ModelSerializer):
    published_user = serializers.StringRelatedField()
    project_files = ProjectFileSerializer(many=True, required=False)
    files = serializers.ListField(write_only=True, required=False, child=serializers.FileField())

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ("published_username",)

    def create(self, validated_data):
        uploaded_files_data = validated_data.pop("files", [])
        skills_data = validated_data.pop("skill_needed", [])
        project = Project.objects.create(**validated_data)
        project.skill_needed.set(skills_data)
        if uploaded_files_data:
            for file in uploaded_files_data:
                ProjectFile.objects.create(project=project, file=file)
        return project

    def update(self, instance, validated_data):
        uploaded_files_data = validated_data.pop("files", [])
        for file in uploaded_files_data:
            ProjectFile.objects.create(project=instance, file=file)
        instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        skills_data = SkillSerializer(instance.skill_needed.all(), many=True).data
        data["skill_needed"] = []
        for item in skills_data:
            skill_info = item["name"]
            data["skill_needed"].append(skill_info)

        if data["published_username"] == "":
            data.pop("published_username", None)
        else:
            data.pop("published_user", None)
        return data


class ProjectWithURLSerializer(ProjectSerializer):
    project_url = serializers.HyperlinkedIdentityField(view_name="projects-detail")


class UserProjectSerializer(ProjectSerializer):
    project_url = serializers.HyperlinkedIdentityField(view_name="user-projects-detail")
    status = serializers.StringRelatedField()

    def validate(self, data):
        min_price = data.get("min_price")
        max_price = data.get("max_price")
        due_date = data.get("due_date")
        proposal_time_end = data.get("proposal_time_end")

        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError(_("Minimum price cannot be greater than maximum price."))

        # x = min_price * Decimal("0.3")
        # if not max_price >= round(x) + min_price:
        #     raise serializers.ValidationError(_(f"Maximum must be at least {min_price + round(x)}."))

        if due_date and due_date < timezone.now().date():
            raise serializers.ValidationError(_("Due date cannot be in the past."))

        if proposal_time_end > due_date:
            raise serializers.ValidationError(_("Proposal time end must be before the due date."))

        return data


class ProjectProposalCreateSerializer(serializers.ModelSerializer):
    proposer = serializers.StringRelatedField()

    class Meta:
        model = ProjectProposal
        exclude = ("project",)
        read_only_fields = ("proposer_username", "is_accepted", "is_canceled")

    def validate(self, data):
        submission_date = data.get("submission_date")
        proposed_price = data.get("proposed_price")
        is_price_adjusted = data.get("is_price_adjusted", False)
        is_date_adjusted = data.get("is_date_adjusted", False)
        due_date = self.context["view"].get_object().due_date if self.context["view"].get_object() else None
        min_price = self.context["view"].get_object().min_price if self.context["view"].get_object() else None
        max_price = self.context["view"].get_object().max_price if self.context["view"].get_object() else None
        published_user = self.context["view"].get_object().published_user if self.context["view"].get_object() else None
        proposer = self.context["request"].user

        if published_user == proposer:
            raise serializers.ValidationError(_("The proposer cannot be the owner of the project."))

        if not is_price_adjusted:
            if proposed_price < min_price or proposed_price > max_price:
                raise serializers.ValidationError(_("Proposed price must be within the project's price range."))
        else:
            if min_price <= proposed_price <= max_price:
                raise serializers.ValidationError(_("Adjusted price should be outside the project's price range."))

        if submission_date and submission_date < timezone.now().date():
            raise serializers.ValidationError(_("Submission date cannot be in the past."))

        if not is_date_adjusted:
            if submission_date and submission_date > due_date:
                raise serializers.ValidationError(_("Submission date must be before the project due date."))
        else:
            if submission_date and submission_date <= due_date:
                raise serializers.ValidationError(_("Adjusted date should be after the project due date."))

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data["proposer_username"] == "":
            data.pop("proposer_username", None)
        else:
            data.pop("proposer", None)
        return data


class ProjectProposalSerializer(ProjectProposalCreateSerializer):
    proposer_profile = serializers.SerializerMethodField()
    proposer_educations = serializers.SerializerMethodField()
    proposer_skills = serializers.SerializerMethodField()
    proposer_experiences = serializers.SerializerMethodField()
    proposer_portfolio = serializers.SerializerMethodField()

    def get_model_links(self, i, model, url_name):
        request = self.context.get("request")
        link = []
        for instance in model.objects.filter(user=i.proposer):
            link.append(reverse(url_name, kwargs={"pk": instance.id}, request=request))
        return link

    def get_proposer_profile(self, i):
        return reverse("user-profile-detail", kwargs={"pk": i.proposer.pk}, request=self.context.get("request"))

    def get_proposer_educations(self, i):
        return self.get_model_links(i, UserEducation, "user-educations-detail")

    def get_proposer_skills(self, i):
        return self.get_model_links(i, UserSkill, "user-skills-detail")

    def get_proposer_experiences(self, i):
        return self.get_model_links(i, UserExperience, "user-experience-detail")

    def get_proposer_portfolio(self, i):
        return self.get_model_links(i, UserPortfolio, "user-portfolio-detail")


class ProjectProposalDetailSerializer(serializers.ModelSerializer):
    proposal_url = serializers.HyperlinkedIdentityField(view_name="user-proposals-detail")
    project = serializers.StringRelatedField()
    proposer = serializers.StringRelatedField()

    class Meta:
        model = ProjectProposal
        fields = "__all__"
        read_only_fields = ("proposer_username", "is_accepted", "is_canceled")

    def validate(self, data):
        submission_date = data.get("submission_date")
        if submission_date and submission_date < timezone.now().date():
            raise serializers.ValidationError({"error": _("Submission date cannot be in the past.")})
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data["proposer_username"] == "":
            data.pop("proposer_username", None)
        else:
            data.pop("proposer", None)
        return data


class UserProjectProposalDetailSerializer(ProjectProposalDetailSerializer):
    project = ProjectSerializer(read_only=True)


class InProgressProposalDetailSerializer(UserProjectProposalDetailSerializer):
    open_dispute = serializers.SerializerMethodField()

    def get_open_dispute(self, obj):
        request = self.context.get("request")
        return reverse("user-proposals-dispute", kwargs={"pk": obj.pk}, request=request)


class ChoosingProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChosenProposal
        fields = ("selected_proposal",)


class ChosenProposalSerializer(serializers.ModelSerializer):
    selected_proposal = UserProjectProposalDetailSerializer()

    class Meta:
        model = ChosenProposal
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.get("selected_proposal", {}).pop("proposal_url", None)
        return data


class UserProjectInProgressSerializer(ChosenProposalSerializer):
    mark_complete = serializers.SerializerMethodField()
    open_dispute = serializers.SerializerMethodField()

    def get_mark_complete(self, obj):
        request = self.context.get("request")
        return reverse("user-projects-complete", kwargs={"pk": obj.project.pk}, request=request)

    def get_open_dispute(self, obj):
        request = self.context.get("request")
        return reverse("user-projects-dispute", kwargs={"pk": obj.project.pk}, request=request)


class OpenDispute(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ("id", "description")


class MarkCompleted(serializers.Serializer):
    completed = serializers.BooleanField(default=False)

    def create(self, validated_data):
        project = self.context["project"]
        completed = validated_data.get("completed")
        if completed:
            project.status = "completed"
            project.save()
            proposal = ChosenProposal.objects.get(project=project).selected_proposal
            proposer = proposal.proposer
            proposer_bid = Bid.objects.get(user=proposer)
            proposer_bid.nb_bid += 1
            proposer_bid.save()
            TransactionLog.objects.create(user=proposer, transaction_type="BIDS_RECEIVED", amount=1,
                                          description=f"Received 1 bid upon completing '{project.title}' project.")
        return project


class SaveUnsavedSerializer(serializers.Serializer):
    Save_Unsaved = serializers.BooleanField(default=False)


class CompleteReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField()
    reviewed_user = serializers.StringRelatedField()
    project = serializers.StringRelatedField()
    rating = serializers.DecimalField(required=True, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                      max_digits=2, decimal_places=1, )
    feedback = serializers.CharField(min_length=20, required=True)
    review_url = serializers.HyperlinkedIdentityField(view_name="complete-review-detail")

    class Meta:
        model = UserReview
        exclude = ("reviewed_user_title",)
