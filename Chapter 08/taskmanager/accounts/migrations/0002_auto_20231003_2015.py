from django.db import migrations


def create_organization(apps, schema_editor):
    Organization = apps.get_model("accounts", "Organization")
    Organization.objects.create(name="Default Organization")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_organization),
    ]
