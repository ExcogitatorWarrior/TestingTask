from django.db import migrations

def create_initial_data(apps, schema_editor):
    Role = apps.get_model("api", "Role")
    BusinessElement = apps.get_model("api", "BusinessElement")
    AccessRoleRule = apps.get_model("api", "AccessRoleRule")

    # Create elements
    elements = ["Users", "Products", "Stores", "Orders", "Access Rules"]
    for name in elements:
        BusinessElement.objects.get_or_create(name=name)

    # Default permissions
    default_permissions = {
        "Admin": dict(read_permission=True, read_all_permission=True,
                      create_permission=True, update_permission=True,
                      update_all_permission=True, delete_permission=True,
                      delete_all_permission=True),
        "Moderator": dict(read_permission=True, read_all_permission=True,
                          create_permission=True, update_permission=True,
                          update_all_permission=False, delete_permission=False,
                          delete_all_permission=False),
        "User": dict(read_permission=True, read_all_permission=False,
                     create_permission=True, update_permission=True,
                     update_all_permission=False, delete_permission=False,
                     delete_all_permission=False),
        "Guest": dict(read_permission=True, read_all_permission=False,
                      create_permission=False, update_permission=False,
                      update_all_permission=False, delete_permission=False,
                      delete_all_permission=False),
    }

    for role in Role.objects.all():
        perms = default_permissions.get(role.name, {})
        for element in BusinessElement.objects.all():
            AccessRoleRule.objects.get_or_create(role=role, element=element, defaults=perms)

class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_order"),
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ]