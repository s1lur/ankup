import logging

from ankup.celery import app
from updater.models import Update
from updater.choices import TaskStatus
from utils import SaltClient

logger = logging.getLogger(__name__)


@app.task
def component_update(update_id):
    update = Update.objects.get(pk=update_id)

    update.status = TaskStatus.PROCESSING
    update.save(update_fields=('status',))

    try:
        salt = SaltClient(login=True)

        jid = salt.run_async(
            tgt=update.device.name,
            fun='state.apply',
            arg=['app_update'],
        )

        results = salt.wait_for_job(jid, timeout=600)
        update.status = TaskStatus.SUCCESS
        update.save(update_fields=('status',))

        return results
    except TimeoutError:
        logger.error('Applying %s on %s timed out', update.version, update.device)
        update.status = TaskStatus.ERROR
        update.save(update_fields=('status',))
        return 'timeout'
    except Exception as e:
        logger.exception('Applying %s on %s failed with error %s', update.version, update.device, e)
        update.status = TaskStatus.ERROR
        update.save(update_fields=('status',))
        return str(e)
