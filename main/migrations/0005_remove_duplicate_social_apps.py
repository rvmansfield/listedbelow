from django.db import migrations


def remove_duplicate_social_apps(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    seen = set()
    for app in SocialApp.objects.filter(provider='google').order_by('id'):
        if 'google' in seen:
            app.delete()
        else:
            seen.add('google')


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_share_link_active'),
        ('socialaccount', '0006_alter_socialaccount_extra_data'),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_social_apps,
            migrations.RunPython.noop,
        ),
    ]
