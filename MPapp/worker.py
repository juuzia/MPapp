import os
from celery import Celery
from celery.result import AsyncResult

from flask import Flask, current_app, url_for
import subprocess as sp #TODO check multiprocessing
from celery.utils.log import get_task_logger #TODO logger

BASH_TIMEOUT = os.environ.get('BASH_TIMEOUT', 1200)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.running = False
    return celery


flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
)
celery = make_celery(flask_app)

def get_status(run_id):
    return AsyncResult(run_id).state

@celery.task
def run_mp_fastq(fq1, fq2, run_id, results_dir):
    sp.call("malaria-profiler profile --dir %s -1 %s -2 %s -p %s -t 1 --txt" % (results_dir, fq1, fq2, run_id), shell=True)

@celery.task
def run_mp_bam(bam, run_id, results_dir):
    sp.call("malaria-profiler profile --dir %s -a %s -p %s -t 1 --txt" % (results_dir, bam, run_id), shell=True)
