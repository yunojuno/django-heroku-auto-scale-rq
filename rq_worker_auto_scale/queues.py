"""
Functions for auto-scaling worker dynos.

This module is used to manage RQ queue depths when running on
Heroku. It examines the number of jobs on each queue configured
in Django's `RQ_QUEUES` settings dictionary, and then updates the
'formation' of dynos based on the jobs waiting to be processed.

The calculation of dynos is very simple - it divides the number
of jobs by the 'auto_scale.step' attribute in the RQ_QUEUES config.

e.g. if the config for a queue looks like:

{
    "default": {
        "auto_scale": {
            "min": 1,    # default = 0
            "max": 10,   # default = 10
            "step": 100  # default = 0 (disabled)
        }
    }
}

The the "default" queue will scale between 1..10 dynos every
100 jobs: so 0-99 will have 1 worker, 100-199 will have
2, and so on. The max/min attributes can be used to prevent
the scaling turning off the queue altogether (0), or trying
to spin up 1,000 dynos.

If the "auto_scale.step" value is set to 0 then it is disabled.

"""
import logging

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
import django_rq

logger = logging.getLogger(__name__)


def formation_cache_key(queue_name: str) -> str:
    return f"RQ_WORKER_FORMATION::{queue_name}"


def get_queue_config(queue_name: str):
    """Return min, max, step settings dictionary for a queue.

    Fills in missing details with defaults (0, 10, 0).

    """
    try:
        config = settings.RQ_QUEUES[queue_name].get("auto_scale", {})
    except KeyError:
        raise ImproperlyConfigured(f"Please check RQ_QUEUES settings for {queue_name}.")
    else:
        return dict(
            min=config.get("min", 0),
            max=config.get("max", 10),
            step=config.get("step", 0),
            size=config.get("size", "standard-1X"),
        )


def get_dyno_count(job_count, min_dynos, max_dynos, step):
    """Return the number of dynos required to process the jobs in the queue."""
    if job_count == 0:
        return max(0, min_dynos)
    else:
        return min(1 + int(job_count / step), max_dynos)


def get_worker_formation(queue_name):
    """Return new worker formation based on dynos required to process existing jobs."""
    queue = django_rq.get_queue(queue_name)
    config = get_queue_config(queue_name)
    dynos = get_dyno_count(queue.count, config["min"], config["max"], config["step"])
    formation = dict(quantity=dynos, size=config["size"], type=queue_name)
    return formation
