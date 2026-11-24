from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Task(models.Model):
    """
    Task model representing a to-do item.
    STRICT BUSINESS FIELDS:
    1. name: CharField (max 100)
    2. date: DateField
    3. task_title: CharField (max 200)
    4. description: TextField
    
    Automatic metadata & relationship:
    - user: ForeignKey to User (Owner)
    - id: AutoField
    - created_at: DateTimeField (auto_now_add=True)
    - updated_at: DateTimeField (auto_now=True)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        verbose_name="User"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
        help_text="Name of the person or assignee (max 100 chars)"
    )
    date = models.DateField(
        verbose_name="Date",
        help_text="Target or due date for the task"
    )
    task_title = models.CharField(
        max_length=200,
        verbose_name="Task Title",
        help_text="Concise title for the task (max 200 chars)"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of the task requirements"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def clean(self):
        super().clean()
        if self.name and not self.name.strip():
            raise ValidationError({'name': 'Name cannot be empty or only whitespace.'})
        if self.task_title and not self.task_title.strip():
            raise ValidationError({'task_title': 'Task Title cannot be empty or only whitespace.'})
        if self.description and not self.description.strip():
            raise ValidationError({'description': 'Description cannot be empty or only whitespace.'})

    def __str__(self):
        return f"{self.task_title} ({self.name})"
