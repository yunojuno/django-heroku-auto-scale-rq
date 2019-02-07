import logging

from django.conf import settings
import requests

logger = logging.getLogger(__name__)
APP_NAME = getenv("HEROKU_APP_NAME")
API_TOKEN = getenv("HEROKU_API_TOKEN")


def apply_formation_updates(updates: list) -> list:
    """Call Heroku Platform API to update dyno formations."""
    # https://devcenter.heroku.com/articles/platform-api-reference#formation-batch-update
    logger.info("Updating RQ worker processes: %s", updates)
    if not APP_NAME:
        logger.debug("HEROKU_APP_NAME not set, ignoring formation updates.")
        return
    if not API_TOKEN:
        logger.debug("HEROKU_API_TOKEN not set, ignoring formation updates.")
        return
    try:
        response = requests.patch(
            url=f"https://api.heroku.com/apps/{APP_NAME}/formation",
            headers={
                "Accept": "application/vnd.heroku+json; version=3",
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"updates": updates},
        )
        return response.json()
    except requests.exceptions.RequestException:
        logger.exception("Heroku formation PATCH update failed.")
