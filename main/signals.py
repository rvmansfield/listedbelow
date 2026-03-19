from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MusicList, ListCollaborator


@receiver(post_save, sender=MusicList)
def create_owner_collaborator(sender, instance, created, **kwargs):
    """Auto-create an owner ListCollaborator record when a MusicList is created."""
    if created:
        ListCollaborator.objects.get_or_create(
            music_list=instance,
            user=instance.created_by,
            defaults={
                'role': ListCollaborator.ROLE_OWNER,
                'added_by': instance.created_by,
            },
        )
