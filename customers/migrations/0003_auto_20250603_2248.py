# c:\python\e-commerce\customers\migrations\0003_auto_20250603_2248.py
from django.db import migrations

def populate_initial_data(apps, schema_editor):
    UserLevel = apps.get_model('customers', 'UserLevel')
    ValidStatus = apps.get_model('customers', 'ValidStatus')
    Division = apps.get_model('customers', 'Division')

    # It's good practice to check if they exist before creating,
    # or use get_or_create if you run this migration multiple times (though usually not needed for bulk_create)
    # For simplicity here, we assume they don't exist yet or that unique constraints will handle it.

    UserLevel.objects.bulk_create([
        UserLevel(name="Admin"),
        UserLevel(name="Penjual"),
        UserLevel(name="Pembeli"),
    ], ignore_conflicts=True) # ignore_conflicts=True is useful if you might rerun
    ValidStatus.objects.bulk_create([
        ValidStatus(name="Valid"),
        ValidStatus(name="Invalid"),
        ValidStatus(name="Pending Verification"),
        ValidStatus(name="Keluar"),
    ], ignore_conflicts=True)
    Division.objects.bulk_create([
        Division(name="Keuangan"),
        Division(name="Kas"),
        Division(name="Pembelian"),
        Division(name="Penjualan"),
        Division(name="SDM"),
        Division(name="N/A"),
    ], ignore_conflicts=True)

class Migration(migrations.Migration):
    dependencies = [
        # This should be the name of your *previous* migration file,
        # likely '0002_division_profile_userlevel_validstatus_and_more'
        ('customers', '0002_division_profile_userlevel_validstatus_and_more'),
    ]
    operations = [
        migrations.RunPython(populate_initial_data),
    ]
