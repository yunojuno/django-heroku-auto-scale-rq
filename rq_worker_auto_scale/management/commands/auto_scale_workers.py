import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ... import auto_scale_rqworkers

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = (
        "Automatically scale worker dyno formation based "
        "on the number of jobs in the queue."
    )

    def add_arguments(self, parser):
        parser.add_argument("queues", nargs="+", help="Names of queues to scale.")

    def handle(self, *args, **options):
        queues = options["queues"]
        if len(queues) == 0:
            logger.info("No queues specified, scaling all configured queues.")
            queues = settings.RQ_QUEUES.keys()
        return auto_scale_rqworkers(*queues)
