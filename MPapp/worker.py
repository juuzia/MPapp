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
def run_mp(ftype, files, run_id, results_dir):
    print(files)
    if ftype=="fastq":
        if len(files)==2:
            tmp = f"-1 {files[0]} -2 {files[1]}"
        else:
            tmp = f"-1 {files[0]}"
    elif ftype=="fasta":
        tmp = f"-f {files[0]}"
    elif ftype in ["bam","cram"]:
        tmp = f"-a {files[0]}"

    sp.call("malaria-profiler profile --dir %s %s -p %s -t 1 --txt" % (results_dir, tmp, run_id), shell=True)

