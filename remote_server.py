import subprocess as sp
import time
import json
import sys
from MPapp.worker import run_mp
import argparse

def cmd_out(cmd,verbose=1):
    res = sp.Popen(cmd,shell=True,stdout=sp.PIPE)
    for l in res.stdout:
        yield l.decode().rstrip()

def run_cmd(cmd,verbose=1,target=None,terminate_on_error=True):
    p = sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout,stderr = p.communicate()

def main(args):
    sys.stderr.write("Starting main loop\n")
    watch_directory = args.remote_directory
    username = args.username
    host = args.host
    processing_dir = args.processing_dir

    def process_run(run_file):
        runs_in_progress.add(run_file)
        sys.stderr.write(f"scp {username}@{host}:{watch_directory}/{run_file} {processing_dir}/")
        run_cmd(f"scp {username}@{host}:{watch_directory}/{run_file} {processing_dir}/")
        conf = json.load(open(run_file))
        for f in conf['files']:
            run_cmd(f"scp {username}@{host}:{f} .")
        print(conf)
        rid = conf['run_id']
        local_file_paths = [f"{processing_dir}/{f.split('/')[-1]}" for f in conf['files']]
        run_mp(
            ftype = conf['ftype'], 
            files = local_file_paths, 
            run_id = conf['run_id'], 
            platform = conf['platform'],
            results_dir = processing_dir,
            threads = args.threads
        )
        
        created_files = {
            "results_txt": f"{processing_dir}/{rid}.results.txt",
            "results_json": f"{processing_dir}/{rid}.results.json",
        }

        completion_json_file = f"{rid}.completed.json"
        json.dump(created_files,open(completion_json_file,"w"))
        run_cmd(f"scp {completion_json_file} {' '.join(created_files.values())}  {username}@{host}:{watch_directory}/")


    runs_in_progress = set()

    while True:
        time.sleep(1)
        for l in cmd_out(f"ssh {username}@{host} 'ls {watch_directory}/*run_file.json'"):
            run_file = l.strip().split("/")[-1]
            if run_file not in runs_in_progress:
                process_run(run_file)

    
parser = argparse.ArgumentParser(description='add required annotations',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--remote-directory',type=str,help='Remote directory to watch for new runs',required = True)
parser.add_argument('--username',type=str,help='Username for remote server',required = True)
parser.add_argument('--host',type=str,help='Host for remote server',required = True)
parser.add_argument('--processing-dir',type=str,help='Directory to store results',required = True)
parser.add_argument('--threads',type=int,help='Number of threads to use',default=1)
parser.set_defaults(func=main)
args = parser.parse_args()
args.func(args)