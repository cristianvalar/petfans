"""
Data migration that detects pets with no PetUser relationship (orphaned pets)
and raises an error listing them so they can be fixed manually via admin.
"""
from django.db import migrations


def detect_orphaned_pets(apps, schema_editor):
    """Warn about active pets that have no associated PetUser records."""
    Pet = apps.get_model('core', 'Pet')
    orphaned = Pet.objects.filter(is_active=True, user_relationships__isnull=True)
    if orphaned.exists():
        details = "\n".join(f"  - {p.name} (id={p.id})" for p in orphaned)
        print(
            f"\nWARNING: Found {orphaned.count()} active pet(s) with no owner.\n"
            f"{details}\n"
            "Fix them via Django admin (add a PetUser with role='owner').\n"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_petweight'),
    ]

    operations = [
        migrations.RunPython(detect_orphaned_pets, migrations.RunPython.noop),
    ]
