from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.main, name='home_page'),
    path('project_list/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('project/<int:id>/edit/', views.project_edit, name='project_edit'),
    path('project/<int:id>/delete/', views.project_delete, name='project_delete'),
    path('project/<int:id>/', views.project_detail, name='project_detail'),

    path('projects/<int:project_id>/tasks/new/', views.task_create, name='task_create'),
    path('task/<int:id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:id>/delete/', views.task_delete, name='task_delete'),
]