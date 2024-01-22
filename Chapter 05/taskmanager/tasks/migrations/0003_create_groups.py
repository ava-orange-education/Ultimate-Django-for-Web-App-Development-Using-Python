from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


def create_groups(apps, schema_editor):
    # create "Author" group with "add_task" permission
    Task = apps.get_model("tasks", "Task")
    content_type = ContentType.objects.get_for_model(Task)

    author_group = Group.objects.create(name="Author")
    add_task_permission, _ = Permission.objects.get_or_create(
        codename="add_tasks", content_type=content_type
    )
    author_group.permissions.add(add_task_permission)

    # create "Editor" group with "change_task" permission
    editor_group = Group.objects.create(name="Editor")
    change_task_permission, _ = Permission.objects.get_or_create(
        codename="change_task", content_type=content_type
    )
    editor_group.permissions.add(change_task_permission)

    # create "Admin" group with all permissions
    admin_group = Group.objects.create(name="Admin")
    all_permissions = Permission.objects.filter(content_type__app_label="tasks")
    admin_group.permissions.set(all_permissions)


class Migration(migrations.Migration):
    dependencies = [
        (
            "tasks",
            "0002_move_archived_to_done",
        ),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
