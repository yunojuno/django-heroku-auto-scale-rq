import logging

from django.core.cache import cache

from .heroku import apply_formation_updates
from .queues import get_queue_config, get_worker_formation, formation_cache_key

logger = logging.getLogger(__name__)

__version__ = "0.1"


def auto_scale_rqworkers(*queues: str) -> list:
    """Appy new process formations for all queue workers."""
    logger.info("Auto-scaling queues: %s", queues)
    updates = []
    for queue_name in queues:
        config = get_queue_config(queue_name)
        if config["step"] == 0:
            logger.debug("Queue '%s' has no step specified, ignoring.", queue_name)
        else:
            formation = get_worker_formation(queue_name)
            cache_key = formation_cache_key(queue_name)
            cached_formation = cache.get(cache_key)
            if formation == cached_formation:
                logger.debug("Worker formation (%s) is unchanged.", queue_name)
            else:
                cache.set(cache_key, formation, 60 * 60)
                updates.append(formation)
    apply_formation_updates(updates)
    return updates
