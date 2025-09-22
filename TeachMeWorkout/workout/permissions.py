from rest_framework import permissions
from datetime import datetime


class ExercisePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        is_tuesday = datetime.now().weekday() == 1
        if is_tuesday:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        is_thursday = datetime.now().weekday() == 3
        if is_thursday and view.action == "destroy":
            return False

        is_friday = datetime.now().weekday() == 4
        if is_friday and view.action == "partial_update":
            return False

        return True
