"""Management command to run backup."""
from django.core.management.base import BaseCommand
from ...backup import RotatingBackup


class Command(BaseCommand):
    """Implement the managment command."""

    help = 'Start the backup process, to be run from a hourly cron job.'

    def handle(self, *args, **options):
        """Run the backup by instantiating the RotatingBackup and call the run method."""
        RotatingBackup().run()
