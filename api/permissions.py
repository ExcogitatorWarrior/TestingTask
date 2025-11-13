from rest_framework.permissions import BasePermission
from .models import AccessRoleRule, BusinessElement, Role

class CanAccessAccessRules(BasePermission):
    """
    Allow Admin always, or roles explicitly given permission for Access Rules.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role.name == "Admin":
            return True

        try:
            element = BusinessElement.objects.get(name="Access Rules")
            rule = AccessRoleRule.objects.get(role=user.role, element=element)
            return rule.read_permission or rule.read_all_permission
        except (BusinessElement.DoesNotExist, AccessRoleRule.DoesNotExist):
            return False

class RoleBasedPermission(BasePermission):

    action_map = {
        'list': ('read_permission', 'read_all_permission'),
        'retrieve': ('read_permission', 'read_all_permission'),
        'create': ('create_permission', None),
        'update': ('update_permission', 'update_all_permission'),
        'partial_update': ('update_permission', 'update_all_permission'),
        'destroy': ('delete_permission', 'delete_all_permission'),
    }

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False  # DRF will return 401

        element_name = getattr(view, 'business_element', None)
        if not element_name:
            return False

        # Admin shortcut
        if user.role.name == "Admin":
            return True

        try:
            rule = AccessRoleRule.objects.get(role=user.role, element__name=element_name)
        except AccessRoleRule.DoesNotExist:
            return False

        action = getattr(view, 'action', None)
        if not action or action not in self.action_map:
            return False

        permission_field, all_permission_field = self.action_map[action]

        if action == 'create' and getattr(rule, permission_field, False):
            return True

        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check for ownership.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        element_name = getattr(view, 'business_element', None)
        if not element_name:
            return False

        if user.role.name == "Admin":
            return True

        try:
            rule = AccessRoleRule.objects.get(role=user.role, element__name=element_name)
        except AccessRoleRule.DoesNotExist:
            return False

        action = getattr(view, 'action', None)
        if not action or action not in self.action_map:
            return False

        permission_field, all_permission_field = self.action_map[action]

        if all_permission_field and getattr(rule, all_permission_field, False):
            return True

        if permission_field and getattr(rule, permission_field, False):
            if hasattr(obj, 'owner') and obj.owner == user:
                return True

        return False

class MockRoleBasedPermission(BasePermission):
    """
    Simulates role-based access control for mock endpoints.
    Returns the rule object, the view can filter the mock list.
    """

    def has_permission(self, request, view):
        user_role = getattr(request.user, "role_id", None)
        if not user_role:
            return False

        try:
            element_pk = BusinessElement.objects.get(name=view.business_element).pk
        except BusinessElement.DoesNotExist:
            return False

        try:
            rule = AccessRoleRule.objects.get(role_id=user_role, element_id=element_pk)
        except AccessRoleRule.DoesNotExist:
            return False

        view.access_rule = rule

        return rule.read_permission or rule.read_all_permission