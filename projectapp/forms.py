from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import now
from datetime import date, timedelta
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'due_date', 'duration', 'priority', 'status']
        widgets = {
            'priority': forms.Select(choices=Task.PRIORITY_CHOICES),
            'status': forms.Select(choices=Task.STATUS_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        # Extract project from kwargs
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        self.fields['due_date'].required = False
        self.fields['duration'].required = False

        # If a project is provided, filter tasks and prepopulate project
        if project:
            # Set the project field as hidden with initial value
            self.fields['project'].initial = project
            self.fields['project'].widget = forms.HiddenInput()

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < now().date():
            raise ValidationError('Due date cannot be in the past.')
        return due_date

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        duration = cleaned_data.get('duration')        
        created_at = self.instance.created_at.date() if self.instance.pk else date.today()

        if not due_date and not duration:
            raise forms.ValidationError("Either due date or duration must be provided.")       
            
        if due_date and duration:
            # Ensure consistency between due_date and duration
            expected_due_date = created_at + timedelta(days=duration)
            if due_date != expected_due_date:
                raise forms.ValidationError(
                    f"Due date ({due_date}) and duration ({duration} days) do not align with the task's creation date ({created_at})."
                )

        return cleaned_data

    def save(self, commit=True):
        # Save the task instance without committing yet
        task = super().save(commit=False)

        # If more custom save logic is required, add it here
        created_at = task.created_at or now()
        if not task.due_date and task.duration:
            task.due_date = created_at.date() + timedelta(days=task.duration)
        elif not task.duration and task.due_date:
            task.duration = (task.due_date - created_at.date()).days
        
        if commit:
            task.save()  # Save the task instance

        return task
    
