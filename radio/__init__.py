import logging

from django.utils.version import get_version
from subprocess import check_output, CalledProcessError

logger = logging.getLogger(__name__)


VERSION = (0, 0, 7, 'beta', 1)

__version__ = get_version(VERSION)

try:
    __git_hash__ = check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode()
except (FileNotFoundError, CalledProcessError):
    __git_hash__ = '0'

__fullversion__ = '{} #{}'.format(__version__,__git_hash__)

logger.info('Trunk-Player Version ' + __fullversion__)
