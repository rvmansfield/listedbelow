from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='musiclist',
            name='invite_only',
        ),
        migrations.AddField(
            model_name='musiclist',
            name='is_public',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, any visitor can view this list without logging in.',
            ),
        ),
    ]
