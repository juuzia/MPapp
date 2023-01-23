import os
from celery import Celery
from celery.result import AsyncResult
import json
from flask import Flask, current_app, url_for
import subprocess as sp #TODO check multiprocessing
from celery.utils.log import get_task_logger #TODO logger
import time 
import shutil

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
def run_mp(ftype, files, run_id, results_dir, platform, threads = 1):
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

    sp.call("malaria-profiler profile --dir %s %s --prefix %s --platform %s -t %s --txt" % (results_dir, tmp, run_id, platform, threads), shell=True)


@celery.task
def remote_profile(ftype, files, run_id, results_dir, platform):
    tmp_dir = f"/tmp/runs/"
    conf = {
        "run_id": run_id,
        "ftype": ftype,
        "platform": platform,
        "files": files
    }
    run_file = f"{tmp_dir}/{run_id}.run_file.json"
    json.dump(conf,open(run_file,"w"))
    server_result_file = f"{tmp_dir}/{run_id}.completed.json"
    while True:
        time.sleep(1)
        if os.path.exists(server_result_file):
            break
    server_result = json.load(open(server_result_file,"r"))
    print(server_result)
    for val in server_result.values():
        local_file_name = val.split("/")[-1]
        shutil.copyfile(f"{tmp_dir}/{local_file_name}",f"{results_dir}/{local_file_name}" )
        os.remove(f"{tmp_dir}/{local_file_name}")
    os.remove(server_result_file)
    os.remove(run_file)