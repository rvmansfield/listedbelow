from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_coop_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='musiclist',
            name='share_link_active',
        ),
    ]
