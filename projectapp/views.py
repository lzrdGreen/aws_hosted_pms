from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.db.models import Q


from django.contrib import messages
import json
from datetime import date
from .models import Project, Task
from .forms import ProjectForm, TaskForm

# Home page
def main(request):
    return render(request, 'projectapp/main.html')


# View to create a new project
def project_create(request):
       
    # Permissions logic
    can_add_project = True
    can_change_project = True
    can_delete_project = True   
    
    if request.method == 'POST':
        if not can_add_project:
            messages.error(request, "Sorry, but a permission is required to create a project")
            return redirect('home_page')        
        
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'projectapp/project_form.html', {
        'form': form,
        'can_add_project': can_add_project,
        'can_change_project': can_change_project
    })

# View to list all projects
def project_list(request):    
    sort_by = request.GET.get('sort', 'title')  # Default sorting by title

    # Base query for projects
    project_results = Project.objects.all()  

    # Permissions logic
    can_add_task = True
    can_change_task = True
    can_delete_task = True
    can_change_project = True
    can_delete_project = True
    can_add_project = True

    context = {
        'project_results': project_results.distinct(),
        'sort_by': sort_by,        
        'can_add_task': can_add_task,
        'can_change_task': can_change_task,
        'can_delete_task': can_delete_task,
        'can_change_project': can_change_project,
        'can_delete_project': can_delete_project,
        'can_add_project': can_add_project,
    }

    return render(request, 'projectapp/project_list_new.html', context)


# Edit project
def project_edit(request, id):    
    project = get_object_or_404(Project, id=id)

    # Permissions logic
    can_add_project = True
    can_change_project = True
    can_delete_project = True
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projectapp/project_form.html', {
        'form': form,
        'can_add_project': can_add_project,
        'can_change_project': can_change_project
    })

# Delete project
def project_delete(request, id):    
    project = get_object_or_404(Project, pk=id)

    if request.method == 'POST':
        project.delete()
        return redirect('project_list')

    # where is project_confirm_delete.html?
    return render(request, 'projectapp/project_confirm_delete.html', {'project': project})

# View the details of the project
def project_detail(request, id):    
    project = get_object_or_404(Project, id=id)

    # Check permissions
    can_add_task = True
    can_change_task = True
    can_delete_task = True
    can_change_project = True
    can_delete_project = True

    sort_by = request.GET.get('sort', 'title') 
    if sort_by == 'priority':
        tasks = project.tasks.all().order_by('-priority')
    elif sort_by == 'due_date':
        tasks = project.tasks.all().order_by('due_date')
    elif sort_by == 'title':
        # tasks = project.tasks.all().order_by(('title').lower())
        tasks = project.tasks.all().annotate(lower_title=Lower('title')).order_by('lower_title')
    else:
        tasks = project.tasks.all()

    # Check for overdue tasks
    for task in tasks:
        task.overdue = task.is_overdue()
    
    
    return render(request, 'projectapp/project_detail.html', {
        'project': project,
        'tasks': tasks,            
        'can_add_task': can_add_task,
        'can_change_task': can_change_task,
        'can_delete_task': can_delete_task,
        'can_change_project': can_change_project,
        'can_delete_project': can_delete_project,        
    })

# View to add a new task a task
def task_create(request, project_id):   
    project = get_object_or_404(Project, id=project_id)
    
    # Permissions logic
    can_add_task = True
    can_add_task = True
    can_change_task = True
    can_delete_task = True
    can_change_project = True
    can_delete_project = True
    can_add_project = True
    
    if request.method == 'POST':
        if not can_add_task:
            messages.error(request, "Sorry, but a permission is required to create a task.")
            return redirect('home_page')
                
        form = TaskForm(request.POST, project=project)  # Pass project to the form
        if form.is_valid():
            task = form.save(commit=False)  # Don't save to the DB yet
            

            # Validate due date
            if task.due_date < date.today():
                form.add_error('due_date', 'Due date cannot be in the past.')
            else:
                task.project = project  # Explicitly link the task to the current project               
                
                
                task.save()  # Now save the task with the project linked
                                
                return redirect('project_detail', project.id)
    else:
        form = TaskForm(initial={'project': project}, project=project)  # Pass project to form

    return render(request, 'projectapp/task_form.html', {
        'form': form, 
        'project': project, 
        'can_add_task': can_add_task, 
        'can_change_task': can_change_task
        })


# Edit task
def task_edit(request, task_id):    
    task = get_object_or_404(Task, id=task_id)
    project = task.project  # Get the project the task belongs to
   
    # Permissions logic
    can_add_task = True
    can_change_task = True
    can_delete_task = True
    can_change_project = True
    can_delete_project = True
    can_add_project = True
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=project)  # Pass project to form
        if form.is_valid():
            task = form.save(commit=False)           
            
            task.save()
            return redirect('project_detail', id=project.id)
    else:
        form = TaskForm(instance=task, project=project)  # Pass project to form

    return render(request, 'projectapp/task_form.html', {
        'form': form, 
        'project': project,
        'task': task,
        'can_add_task': can_add_task, 
        'can_change_task': can_change_task
        })

# Delete task
def task_delete(request, id):    
    task = get_object_or_404(Task, pk=id)
   
    if request.method == 'POST':
        task.delete()
        return redirect('project_detail', id=task.project.id)  

    return render(request, 'projectapp/task_confirm_delete.html', {'task': task}) 

# Task detail view
def task_detail(request, id):    
    task = get_object_or_404(Task, id=id)
    task.overdue = task.is_overdue()  # Check if the task is overdue
    # Check permissions for the current user
    project = task.project
    can_edit_task = True
    can_delete_task = True
    return render(request, 'projectapp/task_detail.html', {
        'task': task,
        'project': project,
        'can_edit_task': can_edit_task,
        'can_delete_task': can_delete_task
    })
