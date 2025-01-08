from django.db import models
from datetime import date, timedelta

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]   

    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(default=1, help_text="Duration in days")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=MEDIUM)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')    
    
    
    def __str__(self):
        return f'{self.title} #(Depends on: {self.parent_task.title if self.parent_task else "None"})'
      
    def is_overdue(self):
        return self.due_date < date.today() and self.status != 'done'

    def save(self, *args, **kwargs):
        if self.due_date and not self.duration:
            # Calculate duration if due_date is provided
            self.duration = (self.due_date - self.created_at.date()).days
        elif self.duration and not self.due_date:
            # Calculate due_date if duration is provided
            self.due_date = self.created_at.date() + timedelta(days=self.duration)
        super().save(*args, **kwargs)
    

    
