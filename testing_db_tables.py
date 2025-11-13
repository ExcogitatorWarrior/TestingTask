#!/usr/bin/env python
# testing_db_tables.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django.setup()

from api.models import BusinessElement, AccessRoleRule, Role

elements = ["Users", "Products", "Stores", "Orders", "Access Rules"]

for name in elements:
    obj, created = BusinessElement.objects.get_or_create(name=name)
    if created:
        print(f"Created BusinessElement: {name}")

default_permissions = {
    "Admin": {
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": True,
        "delete_permission": True,
        "delete_all_permission": True,
    },
    "Moderator": {
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False,
    },
    "User": {
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False,
    },
    "Guest": {
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": False,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False,
    },
}

roles = Role.objects.all()
elements = BusinessElement.objects.all()

for role in roles:
    perms = default_permissions.get(role.name, {})
    for element in elements:
        obj, created = AccessRoleRule.objects.get_or_create(
            role=role,
            element=element,
            defaults=perms
        )
        if created:
            print(f"Created AccessRoleRule for role {role.name} → element {element.name}")

print("✅ All done!")
