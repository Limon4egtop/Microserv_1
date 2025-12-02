from django import forms
from .models import Defect, Comment, Attachment


class DefectForm(forms.ModelForm):
    class Meta:
        model = Defect
        fields = ["project", "stage", "title", "description", "priority", "assignee", "due_date", "status"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def clean_status(self):
        new_status = self.cleaned_data.get("status")
        instance = self.instance
        if instance and instance.pk and not instance.can_transition(new_status):
            raise forms.ValidationError("Недопустимый переход статуса.")
        return new_status


class CommentForm(forms.ModelForm):
    class Meta: model = Comment; fields = ["text"]


class AttachmentForm(forms.ModelForm):
    class Meta: model = Attachment; fields = ["file"]
