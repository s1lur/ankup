#!/bin/sh

for i in $(seq 1 "${CELERY_WORKER_COUNT}"); do
  celery -A ankup worker -l info --concurrency=10 -n "worker${i}"
done
