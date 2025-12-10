import logging
from croniter import croniter

from django.utils import timezone

from ankup.celery import app
from updater.models import Device, AntivirusUpdate
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

        device.save(update_fields=['is_online', 'last_seen'])


@app.task
def check_device_antivirus_updates():
    now = timezone.now()

    devices_to_run = Device.objects.filter(
        antivirus_schedule__isnull=False,
        next_run_at__lte=now
    )

    for device in devices_to_run:
        logger.info(f"Schedule triggering for {device.name}")

        AntivirusUpdate.objects.create(device=device)

        try:
            iter = croniter(device.antivirus_schedule, now)
            next_time = iter.get_next(timezone.datetime)

            device.next_run_at = next_time
            device.save(update_fields=['next_run_at'])

        except Exception as e:
            logger.error(f"Failed to reschedule {device.name}: {e}")
            device.next_run_at = None
            device.save(update_fields=['next_run_at'])
