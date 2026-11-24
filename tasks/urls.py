from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import TaskViewSet

# DRF Router for REST APIs
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task-api')

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Web Frontend URLs
    path('', views.dashboard, name='dashboard'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Export Reports (CSV / PDF)
    path('tasks/export/csv/', views.export_tasks_csv, name='export_csv'),
    path('tasks/export/pdf/', views.export_tasks_pdf, name='export_pdf'),

    # REST API URLs:
    # GET    /api/tasks/        (List all tasks)
    # POST   /api/tasks/        (Create new task)
    # GET    /api/tasks/<id>/   (Retrieve single task)
    # PUT    /api/tasks/<id>/   (Full update task)
    # PATCH  /api/tasks/<id>/   (Partial update task)
    # DELETE /api/tasks/<id>/   (Delete task)
    path('api/', include(router.urls)),
]
