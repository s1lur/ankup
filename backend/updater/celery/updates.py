import logging

from django.apps import apps
from django.db import transaction

from ankup.celery import app
from updater.choices import TaskStatus
from utils import SaltClient

logger = logging.getLogger(__name__)


@app.task
def execute_update(model_name, instance_id, timeout=600):
    model = apps.get_model('updater', model_name)
    instance = model.objects.get(pk=instance_id)
    connections = None
    if instance._connection_model:
        connections = instance._connection_model.objects.filter(applied=False).select_for_update()

    instance.status = TaskStatus.PROCESSING
    instance.save(update_fields=('status',))

    try:
        salt = SaltClient(login=True)

        jid = salt.run_async(
            tgt=instance.device.name,
            fun='state.apply',
            arg=[model._salt_task_name],
        )

        results = salt.wait_for_job(jid, timeout=timeout)
        with transaction.atomic():
            instance.status = TaskStatus.SUCCESS
            instance.save(update_fields=('status',))
            if connections:
                for connection in connections:
                    connection.applied = True
                    connection.save(update_fields=('applied',))

        return results
    except TimeoutError:
        logger.error('Applying %s on %s timed out', instance, instance.device)
        instance.status = TaskStatus.ERROR
        instance.save(update_fields=('status',))
        return 'timeout'
    except Exception as e:
        logger.exception('Applying %s on %s failed with error %s', instance, instance.device, e)
        instance.status = TaskStatus.ERROR
        instance.save(update_fields=('status',))
        return str(e)
