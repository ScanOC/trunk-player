from redis.exceptions import ConnectionError
from radio.utility import RedisQueue


from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Show count of pending transmissions in redis queue'

    def handle(self, *args, **options):
        q = RedisQueue('new_trans')
        try:
            print('Pending transmissions to add {}'.format(q.qsize()))
        except ConnectionError:
            print('Cannot connect to redis is it running?')
            return

