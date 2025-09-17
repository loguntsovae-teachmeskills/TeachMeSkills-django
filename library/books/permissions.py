from rest_framework.permissions import BasePermission


class AuthorPermission(BasePermission):

    def has_permission(self, request, view):
        print("has_permission")
        return True

    def has_object_permission(self, request, view, obj):
        # print("has_object_permission")
        # return request.user == obj.user
        return True