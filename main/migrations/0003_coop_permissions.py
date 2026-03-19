from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_simplify_list_access'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='musiclist',
            name='allow_votes',
        ),
        migrations.RemoveField(
            model_name='musiclist',
            name='allow_adds',
        ),
        migrations.AddField(
            model_name='musiclist',
            name='is_coop',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, any logged-in user with access can add songs and vote.',
            ),
        ),
    ]
