from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Defect, History


@receiver(pre_save, sender=Defect)
def track_changes(sender, instance: Defect, **kwargs):
    if not instance.pk: return
    try:
        prev = Defect.objects.get(pk=instance.pk)
    except Defect.DoesNotExist:
        return
    fields = ["title", "description", "priority", "assignee_id", "due_date", "status", "project_id", "stage_id"]
    for f in fields:
        if getattr(prev, f) != getattr(instance, f):
            History.objects.create(defect=instance, field=f, old_value=str(getattr(prev, f)),
                                   new_value=str(getattr(instance, f)),
                                   changed_by=getattr(instance, "_changed_by", None))
