from django.db import models
from django.conf import settings
from django.utils import timezone
from projects.models import Project, Stage
class Priority(models.TextChoices):
    LOW="LOW","Низкий"; MEDIUM="MED","Средний"; HIGH="HIG","Высокий"
class Status(models.TextChoices):
    NEW="NEW","Новая"; IN_PROGRESS="INP","В работе"; IN_REVIEW="REV","На проверке"; CLOSED="CLO","Закрыта"; CANCELED="CAN","Отменена"
ALLOWED_TRANSITIONS={
    Status.NEW:[Status.IN_PROGRESS,Status.CANCELED],
    Status.IN_PROGRESS:[Status.IN_REVIEW,Status.CANCELED],
    Status.IN_REVIEW:[Status.CLOSED,Status.IN_PROGRESS],
    Status.CLOSED:[], Status.CANCELED:[],
}
class Defect(models.Model):
    project=models.ForeignKey(Project,on_delete=models.PROTECT,related_name="defects",verbose_name="Объект")
    stage=models.ForeignKey(Stage,on_delete=models.SET_NULL,null=True,blank=True,related_name="defects",verbose_name="Этап")
    title=models.CharField("Заголовок",max_length=255)
    description=models.TextField("Описание",blank=True)
    priority=models.CharField("Приоритет",max_length=3,choices=Priority.choices,default=Priority.MEDIUM)
    assignee=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="assigned_defects",verbose_name="Исполнитель")
    reporter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="reported_defects",verbose_name="Автор")
    due_date=models.DateField("Срок",null=True,blank=True)
    status=models.CharField("Статус",max_length=3,choices=Status.choices,default=Status.NEW)
    created_at=models.DateTimeField("Создано",auto_now_add=True)
    updated_at=models.DateTimeField("Обновлено",auto_now=True)
    class Meta: ordering=["-created_at"]
    def __str__(self): return f"[{self.get_status_display()}] {self.title}"
    def can_transition(self,new_status):
        if not self.pk: return True
        allowed=ALLOWED_TRANSITIONS.get(self.status,[])
        return new_status in allowed or new_status==self.status
class Comment(models.Model):
    defect=models.ForeignKey(Defect,on_delete=models.CASCADE,related_name="comments")
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
class Attachment(models.Model):
    defect=models.ForeignKey(Defect,on_delete=models.CASCADE,related_name="attachments")
    file=models.FileField(upload_to="attachments/%Y/%m/%d")
    uploaded_at=models.DateTimeField(auto_now_add=True)
    uploaded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
class History(models.Model):
    defect=models.ForeignKey(Defect,on_delete=models.CASCADE,related_name="history")
    field=models.CharField(max_length=100)
    old_value=models.TextField(blank=True,null=True)
    new_value=models.TextField(blank=True,null=True)
    changed_at=models.DateTimeField(default=timezone.now)
    changed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    class Meta: ordering=["-changed_at"]
