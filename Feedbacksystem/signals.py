from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

@receiver(post_save, sender=User)
def assign_admin_group(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        # Try to get the group named 'admin'
        admin_group, group_created = Group.objects.get_or_create(name='admin')
        # Add the user to the 'admin' group
        instance.groups.add(admin_group)
