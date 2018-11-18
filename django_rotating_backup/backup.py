"""Rotating backup script Django databases and Media files."""

import glob
import gzip
import logging
import os
import sqlite3
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path
from shutil import copyfile

from django.conf import settings

from .exceptions import DRBConfigException

logger = logging.getLogger('django_rotating_backup')
logger.setLevel(logging.INFO)
log_console = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
log_console.setFormatter(formatter)
logger.addHandler(log_console)


class RotatingBackup:
    """Main Class for Rotating Backup."""

    # destination_folder = None
    hourly_folder = 'hourly'
    daily_folder = 'daily'
    weekly_folder = 'weekly'
    monthly_folder = 'monthly'

    # hours_to_keep = None
    # days_to_keep = None
    # weeks_to_keep = None
    # months_to_keep = None
    #
    # sqlite_backup_copy_enabled = False
    # database_dumps_enabled = False
    # media_backups_enabled = False
    # remote_sync_enabled = False

    sqlite_backup_copy_extension = 'sqlite3'
    database_dump_extension = 'sql.gz'
    media_backup_extension = 'tar.gz'

    # rsync_host = None
    # rsync_remote_path = None
    # rsync_user = None
    # rsync_pub_key = None

    now = datetime.now()

    def __init__(self):
        """Initialise the RotatingBackup class."""
        logger.debug('Start Initialisation.')
        self.parse_settings()
        timestamp = self.now.strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'Backup started at: {timestamp}')

    def parse_settings(self):
        """Parse settings from environment or Django settings."""
        try:
            self.hours_to_keep = int(os.environ.get('DRB_BACKUP_HOURS_TO_KEEP', settings.DRB_BACKUP_HOURS_TO_KEEP))
            self.days_to_keep = int(os.environ.get('DRB_BACKUP_DAYS_TO_KEEP', settings.DRB_BACKUP_DAYS_TO_KEEP))
            self.weeks_to_keep = int(os.environ.get('DRB_BACKUP_WEEKS_TO_KEEP', settings.DRB_BACKUP_WEEKS_TO_KEEP))
            self.months_to_keep = int(os.environ.get('DRB_BACKUP_MONTHS_TO_KEEP', settings.DRB_BACKUP_MONTHS_TO_KEEP))

            self.destination_folder = os.environ.get('DRB_DESTINATION_FOLDER', settings.DRB_DESTINATION_FOLDER)

            self.sqlite_backup_copy_enabled = os.environ.get('DRB_ENABLE_SQLITE_BACKUP_COPY',
                                                             settings.DRB_ENABLE_SQLITE_BACKUP_COPY)
            self.database_dumps_enabled = os.environ.get('DRB_ENABLE_DATABASE_DUMPS',
                                                         settings.DRB_ENABLE_DATABASE_DUMPS)
            self.media_backups_enabled = os.environ.get('DRB_ENABLE_MEDIA_BACKUPS', settings.DRB_ENABLE_MEDIA_BACKUPS)

            self.remote_sync_enabled = os.environ.get('DRB_ENABLE_REMOTE_SYNC', settings.DRB_ENABLE_REMOTE_SYNC)
            if self.remote_sync_enabled:
                self.rsync_host = os.environ.get('DRB_RSYNC_HOST', settings.DRB_RSYNC_HOST)
                self.rsync_remote_path = os.environ.get('DRB_RSYNC_REMOTE_PATH', settings.DRB_RSYNC_REMOTE_PATH)
                self.rsync_user = os.environ.get('DRB_RSYNC_USER', settings.DRB_RSYNC_USER)
                self.rsync_pub_key = os.environ.get('DRB_RSYNC_PUB_KEY', settings.DRB_RSYNC_PUB_KEY)

        except AttributeError as error:
            raise DRBConfigException(f'Please verify if all settings have been correctly specified, error: {error}')

    #
    # Helper Methods
    #

    @staticmethod
    def is_sqlite(database):
        """Check if database is a SQLite3 db."""
        return settings.DATABASES[database]['ENGINE'].endswith('sqlite3')

    @staticmethod
    def is_postgresql(database):
        """Check if database is a PostgreSQL db."""
        return settings.DATABASES[database]['ENGINE'].endswith('postgresql')

    @staticmethod
    def create_destination_folder(destination_folder=None):
        """Check if backup destination exists and create it if not."""
        if not os.path.exists(destination_folder):
            Path(f'{destination_folder}').mkdir(parents=True, exist_ok=True)
            logger.info(f'Destination folder `{destination_folder}` did not exist and has been created.')
        else:
            logger.info(f'Using existing destination folder: `{destination_folder}`')

    @staticmethod
    def list_files_ordered_by_timestamp(destination=None, name=None, extension=None):
        """Return a list of files ordered by create timestamp."""
        files = glob.glob(f'{destination}/{name}_*.{extension}')
        files.sort(key=os.path.getmtime)  # Sort by create time
        return files

    def delete_old_files(self, destination=None, name=None, extension=None, number_to_keep=1):
        """Delete all old files which are extending the set retention."""
        files = self.list_files_ordered_by_timestamp(destination=destination, name=name, extension=extension)
        for file in files[:-number_to_keep]:
            os.remove(file)
            logger.info(f'Removed: {file}')

    @staticmethod
    def file_exists(destination=None, name=None, pattern=None, extension=None):
        """Check if a file exists."""
        if os.path.isfile(f'{destination}/{name}_{pattern}.{extension}'):
            logger.info(f'File {destination}/{name}_{pattern}.{extension} already exists, skipping...')
            return True
        return False

    def copy_backup(self, destination=None, name=None, pattern=None, extension=None, source=None):
        """Copy a file."""
        self.create_destination_folder(destination_folder=destination)
        target = f'{destination}/{name}_{pattern}.{extension}'
        copyfile(source, target)
        logger.info(f'Created copy of `{source}` to `{target}`')

    #
    # Backup methods
    #

    def make_sqlite_backup_copy(self, destination=None, name=None, pattern=None):
        """Make a database backup."""
        backup_filename = f'{name}_{pattern}.{self.sqlite_backup_copy_extension}'
        copyfile(settings.DATABASES[name]['NAME'], f'{destination}/{backup_filename}')
        logger.info(f'Made copy of SQLite database `{name}` to `{destination}/{backup_filename}`')
        return f'{destination}/{backup_filename}'

    def make_database_dump(self, destination=None, name=None, pattern=None):
        """Make a database SQL dump."""
        dump_filename = f'{name}_{pattern}.{self.database_dump_extension}'

        if self.is_sqlite(name):
            conn = sqlite3.connect(settings.DATABASES[name]['NAME'])
            with gzip.open(f'{destination}/{dump_filename}', 'wb') as backup_file:
                for line in conn.iterdump():
                    backup_file.write(str(f'{line}\n').encode('utf-8'))
            logger.info(f'Created SQLite dump of database `{name}` to `{destination}/{dump_filename}`')

        if self.is_postgresql(name):
            with gzip.open(f'{destination}/{dump_filename}', 'wb') as backup_file:
                host = settings.DATABASES[name]['HOST'] if not settings.DATABASES[name]['HOST'] == '' else '127.0.0.1'
                port = settings.DATABASES[name]['PORT'] if not settings.DATABASES[name]['PORT'] == '' else '5432'

                cmd = ['sh', '-c', 'PGPASSWORD=' + str(settings.DATABASES[name]['PASSWORD']) + ' pg_dump -h ' + host +
                       ' -p ' + port + ' -U ' + settings.DATABASES[name]['USER'] + ' ' +
                       settings.DATABASES[name]['NAME']]
                popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

                for stdout_line in iter(popen.stdout.readline, ''):
                    backup_file.write(stdout_line.encode('utf-8'))

                popen.stdout.close()
                popen.wait()
            logger.info(f'Created PostgreSQL dump of database `{name}` to `{destination}/{dump_filename}`')

        return f'{destination}/{dump_filename}'

    def make_media_backup(self, destination=None, pattern=None):
        """Make a media backup."""
        media_backup_filename = f'media_{pattern}.{self.media_backup_extension}'
        with tarfile.open(f'{destination}/{media_backup_filename}', "w:gz") as backup_file:
            for file in glob.iglob(f'{settings.MEDIA_ROOT}/**', recursive=True):
                backup_file.add(file)
            backup_file.close()
        logger.info(f'Created Media backup of `{settings.MEDIA_ROOT}` to `{destination}/{media_backup_filename}`')
        return f'{destination}/{media_backup_filename}'

    #
    # Main Rotating logic
    #

    def archive(self, backup_file=None):
        """Archive the files with respect to retention settings."""
        schema = {
            'daily': {
                'pattern': self.now.strftime('%Y-%m-%d'),
                'destination': f'{self.destination_folder}/{self.daily_folder}',
                'retention': self.days_to_keep
            },
            'weekly': {
                'pattern': self.now.strftime('%Y-%V'),
                'destination': f'{self.destination_folder}/{self.weekly_folder}',
                'retention': self.weeks_to_keep
            },
            'monthly': {
                'pattern': self.now.strftime('%Y-%b'),
                'destination': f'{self.destination_folder}/{self.monthly_folder}',
                'retention': self.months_to_keep
            }
        }

        file_name = backup_file.split('/')[-1]
        name = file_name.split('_', 1)[0]
        extension = backup_file.split('.', 1)[1]

        for key, value in schema.items():
            logger.info(f'Running rotation scheme `{key}` for `{name}`')
            if not self.file_exists(destination=value['destination'], name=name, pattern=value['pattern'],
                                    extension=extension):
                self.copy_backup(destination=value['destination'], name=name, pattern=value['pattern'],
                                 extension=extension, source=backup_file)
                self.delete_old_files(destination=value['destination'], name=name,
                                      extension=extension, number_to_keep=value['retention'])

    def sync_remote(self):
        """Synchronise the remote server with local backup files."""
        with open('/tmp/drb_ssh_pub_key', 'w') as ssh_pub_key_file:
            ssh_pub_key_file.write(self.rsync_pub_key)

        command = f'rsync -avz -e "ssh -i /tmp/drb_ssh_pub_key -o StrictHostKeyChecking=no ' \
                  f'-o UserKnownHostsFile=/dev/null" ' \
                  f'{self.destination_folder} {self.rsync_user}@{self.rsync_host}:{self.rsync_remote_path} ' \
                  f'--stats -z'
        sync_result = subprocess.run(['sh', '-c', command], stdout=subprocess.PIPE).stdout.decode('utf-8')
        logger.info(f'Sync result: \n{sync_result}')

        os.remove('/tmp/drb_ssh_pub_key')

    def run(self):
        """Run the actual hourly backup."""
        hour_pattern = self.now.strftime('%Y-%m-%d_%H')

        # Create an hourly backup
        destination = f'{self.destination_folder}/{self.hourly_folder}'
        self.create_destination_folder(destination_folder=destination)

        for database in settings.DATABASES.keys():
            # Make SQLite database copy
            if self.is_sqlite(database) and self.sqlite_backup_copy_enabled and not \
                    self.file_exists(destination=destination, name=database, pattern=hour_pattern,
                                     extension=self.sqlite_backup_copy_extension):
                backup_file = self.make_sqlite_backup_copy(destination=destination, name=database, pattern=hour_pattern)
                self.delete_old_files(destination=destination, name=database,
                                      extension=self.sqlite_backup_copy_extension, number_to_keep=self.hours_to_keep)
                self.archive(backup_file=backup_file)

            # Make SQLite database dump
            if self.is_sqlite(database) and self.database_dumps_enabled and not \
                    self.file_exists(destination=destination, name=database, pattern=hour_pattern,
                                     extension=self.database_dump_extension):
                backup_file = self.make_database_dump(destination=destination, name=database, pattern=hour_pattern)
                self.delete_old_files(destination=destination, name=database,
                                      extension=self.database_dump_extension, number_to_keep=self.hours_to_keep)
                self.archive(backup_file=backup_file)

            # Make PostgreSQL dump
            if self.is_postgresql(database) and self.database_dumps_enabled and not \
                    self.file_exists(destination=destination, name=database, pattern=hour_pattern,
                                     extension=self.database_dump_extension):
                backup_file = self.make_database_dump(destination=destination, name=database, pattern=hour_pattern)
                self.delete_old_files(destination=destination, name=database,
                                      extension=self.database_dump_extension, number_to_keep=self.hours_to_keep)
                self.archive(backup_file=backup_file)

            # Give warning for unsupported database types
            if not (self.is_sqlite(database) or self.is_postgresql(database)):
                database_type = settings.DATABASES[database]['ENGINE'].split('.')[-1]
                logger.warning(f'Database `{database}` is not supported as the type is `{database_type}`')

        # Backup Media folder
        if self.media_backups_enabled and not self.file_exists(destination=destination, name='media',
                                                               pattern=hour_pattern,
                                                               extension=self.media_backup_extension):
            # Make media backup
            backup_file = self.make_media_backup(destination=destination, pattern=hour_pattern)
            self.delete_old_files(destination=destination, name='media', extension=self.media_backup_extension,
                                  number_to_keep=self.hours_to_keep)
            self.archive(backup_file=backup_file)

        # Call sync
        if self.remote_sync_enabled:
            self.sync_remote()

        # Finish backup
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'Backup finished at: {timestamp}')
