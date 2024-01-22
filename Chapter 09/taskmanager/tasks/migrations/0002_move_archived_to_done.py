from django.db import migrations


def change_archived_tasks(apps, schema_editor):
    # Get the Task model from the apps registry
    #  the app registry is used to ensure that you're
    # working with the correct version of your model
    Task = apps.get_model("tasks", "Task")
    # Update all 'Archived' tasks to 'Done'
    Task.objects.filter(status="ARCHIVED").update(status="DONE")


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(change_archived_tasks),
    ]
