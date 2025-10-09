from django.db import models
class Project(models.Model):
    name = models.CharField("Название", max_length=255)
    address = models.CharField("Адрес", max_length=255, blank=True)
    description = models.TextField("Описание", blank=True)
    def __str__(self): return self.name
class Stage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stages", verbose_name="Объект")
    name = models.CharField("Этап", max_length=255)
    start_date = models.DateField("Начало", blank=True, null=True)
    end_date = models.DateField("Окончание", blank=True, null=True)
    def __str__(self): return f"{self.project} — {self.name}"
