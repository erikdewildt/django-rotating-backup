# Django-Rotating-Backup

This is a simple app to create rotating backups from the Django database and Media files.


## Quick start

1. Install django-rotating-backups using pip:

	```
	pip install django-rotating-backup
	```
	
2. Add "django-rotating-backups" to your INSTALLED_APPS setting like this:

	```
	INSTALLED_APPS = [
	    ...
	    'django_rotating_backup',
	]
	```

3. Add `python manage.py create_backup` to a hourly cron job.

4. Add settings to the django settings or use environment settings. Please not that environment variables have precedent
over the settings configured in the settings.


## Settings

|Name|Description|
|----|-----------|
|DRB_BACKUP_HOURS_TO_KEEP|The number of hourly backups to keep|
|DRB_BACKUP_DAYS_TO_KEEP|The number of daily backups to keep|
|DRB_BACKUP_WEEKS_TO_KEEP|The number of weekly backups to keep|
|DRB_BACKUP_MONTHS_TO_KEEP|The number of monthly backups to keep|
|DRB_DESTINATION_FOLDER|Where to store the backups|
|DRB_ENABLE_SQLITE_BACKUP_COPY|Set to `True` to make backup copies for SQLite databases|
|DRB_ENABLE_DATABASE_DUMPS|Set to `True` to enable SQL dumps of databases|
|DRB_ENABLE_MEDIA_BACKUPS|Set to `True` to enable Media folder backups|
|DRB_ENABLE_REMOTE_SYNC|Set to `True` to enable remote sync of backup files|
|DRB_RSYNC_HOST|The remote host where to sync to|
|DRB_RSYNC_REMOTE_PATH|The path on the remote server|
|DRB_RSYNC_USER|The user to connect as|
|DRB_RSYNC_PUB_KEY|The ssh public key to use|

## Example

```
...
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
...

# Settings for Django Rotating Backup
DRB_BACKUP_HOURS_TO_KEEP = 24
DRB_BACKUP_DAYS_TO_KEEP = 7
DRB_BACKUP_WEEKS_TO_KEEP = 4
DRB_BACKUP_MONTHS_TO_KEEP = 3

DRB_DESTINATION_FOLDER = os.path.join(BASE_DIR, 'backups')

DRB_ENABLE_SQLITE_BACKUP_COPY = True
DRB_ENABLE_DATABASE_DUMPS = True
DRB_ENABLE_MEDIA_BACKUPS = True

DRB_ENABLE_REMOTE_SYNC = True
DRB_RSYNC_HOST = '192.168.2.6'
DRB_RSYNC_REMOTE_PATH = '/home/backupuser/backup/'
DRB_RSYNC_USER = 'backupuser'
DRB_RSYNC_SSH_KEY = '/Users/backupuser/.ssh/id_rsa'
```
