from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    """
    DRF Serializer for the Task model.
    Enforces the four business fields: name, date, task_title, description.
    Metadata fields (id, user, created_at, updated_at) are read-only.
    """
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Task
        fields = [
            'id',
            'user',
            'name',
            'date',
            'task_title',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Name cannot be empty or only whitespace.")
        return stripped

    def validate_task_title(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Task Title cannot be empty or only whitespace.")
        return stripped

    def validate_description(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Description cannot be empty or only whitespace.")
        return stripped
