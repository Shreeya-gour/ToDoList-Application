from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    Complete REST API ViewSet for Task operations.
    
    Supported HTTP Methods:
    - GET /api/tasks/           : List all tasks
    - POST /api/tasks/          : Create a new task (201 Created)
    - GET /api/tasks/<id>/      : Retrieve task details (200 OK / 404)
    - PUT /api/tasks/<id>/      : Full update of all fields (200 OK / 400 / 404)
    - PATCH /api/tasks/<id>/    : Partial update of specific fields (200 OK / 400 / 404)
    - DELETE /api/tasks/<id>/   : Delete task record (204 No Content / 404)
    """
    queryset = Task.objects.all().order_by('-date', '-created_at')
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'task_title', 'description']
    ordering_fields = ['date', 'created_at', 'task_title', 'name']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        """User-specific API query isolation"""
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user).order_by('-date', '-created_at')
        return Task.objects.all().order_by('-date', '-created_at')

    def perform_create(self, serializer):
        """Automatically attach task to authenticated user"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    def create(self, request, *args, **kwargs):
        """POST /api/tasks/ - Create a task with validation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """PUT /api/tasks/<id>/ - Full update (all required fields required)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/tasks/<id>/ - Partial update"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/tasks/<id>/ - Delete task"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Task '{instance.task_title}' was successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )
