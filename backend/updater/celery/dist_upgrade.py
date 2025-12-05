import logging
from ankup.celery import app
from updater.models import DistUpgrade
from updater.choices import TaskStatus
from utils import SaltClient

logger = logging.getLogger(__name__)

@app.task
def dist_upgrade(dist_upgrade_id):
    dist_upgrade = DistUpgrade.objects.filter(pk=dist_upgrade_id)
    dist_upgrade.status = TaskStatus.PROCESSING
    dist_upgrade_id.save(update_fields=('status',))

    try:
        salt = SaltClient(login=True)

        jid = salt.run_async(
            tgt=dist_upgrade_id.device.name,
            fun='state.apply',
            arg=['dist_upgrade'],
        )

        results = salt.wait_for_job(jid, timeout=1800)
        dist_upgrade.status = TaskStatus.SUCCESS
        dist_upgrade.save(update_fields=('status',))

        return results
    except TimeoutError:
        logger.error('Running dist-upgrade on %s timed out', dist_upgrade.device)
        dist_upgrade.status = TaskStatus.ERROR
        dist_upgrade.save(update_fields=('status',))
        return 'timeout'
    except Exception as e:
        logger.error('Running dist-upgrade on %s failed with error %s', dist_upgrade.device, e)
        dist_upgrade.status = TaskStatus.ERROR
        dist_upgrade.save(update_fields=('status',))
        return str(e)
