"""Custom Exceptions for Django Rotating Backup."""
import logging

logger = logging.getLogger('django_rotating_backup')


class DRBException(Exception):
    pass


class DRBConfigException(DRBException):

    def __init__(self, message):
        """Initialise DRBConfigException."""
        super().__init__(message)
        logger.error(f'Configuration error round: {message}')
