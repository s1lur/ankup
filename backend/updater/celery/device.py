import logging

from django.utils import timezone

from ankup.celery import app
from updater.models import Device
from utils import SaltClient

logger = logging.getLogger(__name__)


@app.task
def update_devices_availability():
    devices = Device.objects.all()
    if not devices.exists():
        return

    all_names = [d.name for d in devices]

    try:
        client = SaltClient(login=True)
        raw_results = client.ping_minions(target=all_names)
    except Exception as e:
        logger.error("Salt API Error: %s", e)
        return

    for device in devices:
        is_up = raw_results.get(device.name, False)

        if is_up:
            device.is_online = True
            device.last_seen = timezone.now()
        else:
            device.is_online = False

        device.save(update_fields=['is_up', 'last_seen'])
