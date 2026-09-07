"""
Custom permissions for Book Summary Platform.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only owner can edit/delete; public summaries are readable by anyone."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, "is_public") and not obj.is_public:
                return obj.user == request.user
            return True
        return obj.user == request.user


class IsBookSummaryOwner(permissions.BasePermission):
    """Only the summary owner can update/delete."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if not obj.is_public:
                return obj.user == request.user
            return True
        return obj.user == request.user


class IsAuthenticatedOrReadOnlyForPublic(permissions.BasePermission):
    """POST/PUT/DELETE require auth; GET allowed for public content."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
