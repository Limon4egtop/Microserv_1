from django.contrib.auth.models import AbstractUser
from django.db import models
class Roles(models.TextChoices):
    MANAGER = "MAN", "Менеджер"
    ENGINEER = "ENG", "Инженер"
    VIEWER = "VWR", "Наблюдатель"
class User(AbstractUser):
    role = models.CharField(max_length=3, choices=Roles.choices, default=Roles.ENGINEER)
    @property
    def is_manager(self): return self.role == Roles.MANAGER
    @property
    def is_engineer(self): return self.role == Roles.ENGINEER
    @property
    def is_viewer(self): return self.role == Roles.VIEWER
    def __str__(self): return f"{self.username} ({self.get_role_display()})"
