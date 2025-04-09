"""Create groups, permissions and users."""

import logging
import os

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

GROUPS = ["currencies-provider-management-grp"]
MODELS = ["exchange rate provider", "currency"]
PERMISSIONS = ["view", "add", "delete", "change"]


def create_group_with_permissions():
    """Create the groups and set their permissions."""
    for group in GROUPS:
        created_group, created = Group.objects.get_or_create(name=group)
        if created:
            logging.info("The group {} has been created.".format(group))
        for model in MODELS:
            for permission in PERMISSIONS:
                grant_command = "Can {} {}".format(permission, model)
                logging.info(grant_command)

                try:
                    model_add_perm = Permission.objects.get(name=grant_command)
                except Permission.DoesNotExist:
                    logging.warning(
                        "Permission not found with name '{}'.".format(
                            grant_command
                        )
                    )
                    continue

                created_group.permissions.add(model_add_perm)


def create_users():
    """Create the default users.

    1 super user.
    1 manager staff not super user.
    """
    user_admin = User.objects.create_superuser(
        os.getenv("DJANGO_SUPERUSER_NAME"),
        os.getenv("DJANGO_SUPERUSER_EMAIL"),
        os.getenv("DJANGO_SUPERUSER_PASSWORD"),
    )
    user_manager = User.objects.create_user(
        os.getenv("DJANGO_APP_EXCHANGE_RATE_MANAGER_NAME"),
        "",
        os.getenv("DJANGO_APP_EXCHANGE_RATE_MANAGER_PASSWORD"),
    )
    user_manager.is_staff = True
    for group in GROUPS:
        Group.objects.filter(name=group).first().user_set.add(user_manager)
    user_admin.save()
    user_manager.save()


class Command(BaseCommand):
    """Provide a CLI option for manage.py to automate the users creation process.

    Args:
        BaseCommand (_type_): _description_
    """

    help = (
        "Creates the group responsible of managing the providers and"
        " currencies"
    )

    def handle(self, *args, **options):
        """Handle the manage py command."""
        create_group_with_permissions()
        logging.info("Created group with permissions.")

        create_users()
        logging.info("Created super user and manager user.")
