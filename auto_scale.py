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
from django.core.exceptions import ImproperlyConfigured
import django_rq
import requests

logger = logging.getLogger(__name__)


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
        )


def get_worker_formation(queue_name, queue_config):
    """Return new worker formation based on dynos required to process existing jobs."""
    queue = django_rq.get_queue(queue_name)
    if queue.count == 0:
        dynos = max(0, queue_config["min"])
    else:
        dynos = min(1 + int(queue.count / queue_config["step"]), queue_config["max"])
    return dict(quantity=dynos, size="standard-1X", type=queue_name)


def auto_scale_rqworkers(*queues: str) -> list:
    """Appy new process formations for all queue workers."""
    logger.info("Auto-scaling queues: %s", queues)
    updates = []
    for queue_name in queues:
        config = get_queue_config(queue_name)
        if config["step"] == 0:
            logger.debug("Queue '%s' has no step specified, ignoring.", queue_name)
        else:
            formation = get_worker_formation(queue_name, config)
            updates.append(formation)
    # this is deliberately _not_ queued up - as it's not blocking any user interaction,
    # and it's not a side-effect.
    _apply_formation_updates(updates)
    return updates


def _apply_formation_updates(updates: list) -> list:
    """Call Heroku Platform API to update dyno formations."""
    # https://devcenter.heroku.com/articles/platform-api-reference#formation-batch-update
    logger.info("Updating RQ worker processes: %s", updates)
    if not settings.HEROKU_APP_NAME:
        logger.debug("HEROKU_APP_NAME not set, ignoring formation updates.")
        return
    if not settings.HEROKU_API_TOKEN:
        logger.debug("HEROKU_API_TOKEN not set, ignoring formation updates.")
        return
    try:
        response = requests.patch(
            url=f"https://api.heroku.com/apps/{settings.HEROKU_APP_NAME}/formation",
            headers={
                "Accept": "application/vnd.heroku+json; version=3",
                "Authorization": f"Bearer {settings.HEROKU_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"updates": updates},
        )
        return response.json()
    except requests.exceptions.RequestException:
        logger.exception("Heroku formation PATCH update failed.")
