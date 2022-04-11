import os
from celery import Celery

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

@celery.task
def run_mp_fastq(fq1, fq2, run_id, results_dir):
    sp.call("malaria-profiler --dir %s profile -1 %s -2 %s -p %s -t 2 --txt" % (results_dir, fq1, fq2, run_id), shell=True)
    #sp.call("wc -l > %s/%s.results.txt" % (fq1, results_dir, run_id), shell=True)

@celery.task
def run_mp_bam(bam, run_id, results_dir):
    #sp.call("echo 0 > %s/%s.results.txt" % (result_dir, run_id), shell=True)
    sp.call("malaria-profiler --dir %s profile -a %s -p %s -t 2 --txt" % (results_dir, bam, run_id), shell=True)


# TODO handling celery process
#https://stackoverflow.com/questions/9034091/how-to-check-task-status-in-celery
#https://gist.github.com/1beb/2a0ea9929a3a414126856bcdc3fa5b2c
#@app.task
# def run(cmd, maksi=None):
# 	if maksi and int(maksi) > 0: BASH_TIMEOUT = maksi

# 	popen = sp.Popen(["exec " + cmd], stdout=sp.PIPE, shell=True);
# 	pid = popen.pid
# 	sttime = time.time()
# 	waittime =  int(BASH_TIMEOUT)

# 	while True:
# 		popen.poll();
# 		time.sleep(1)
# 		rcode = popen.returncode
# 		now = time.time()
# 		if rcode != None:
# 			print("Process finished!")
# 			run.update_state(state=states.SUCCESS)

# 			return popen.stdout.read()

# 		if ( now > (sttime + waittime) ) :
# 			popen.kill()
# 			run.update_state(state=states.FAILURE)
# 			print("Process killed!")
# 			break
