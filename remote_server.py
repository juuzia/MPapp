import subprocess as sp
import time
import json
import sys
from MPapp.worker import run_mp
import argparse
import os


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
    err_dir = args.errlog_dir

    def process_run(run_file):
        runs_in_progress.add(run_file)
        sys.stderr.write(f"scp {username}@{host}:{watch_directory}/{run_file} {processing_dir}/\n")
        run_cmd(f"scp {username}@{host}:{watch_directory}/{run_file} {processing_dir}/")
        conf = json.load(open(f"{processing_dir}/{run_file}"))

        rid = conf['run_id']
        results_json_path = f"{processing_dir}/{rid}.results.json"
        results_txt_path = f"{processing_dir}/{rid}.results.txt"
        results_bam_path = f"{processing_dir}/{rid}.bam"
        results_bam_bai_path = f"{processing_dir}/{rid}.bam.bai"
        
        for f in conf['files']:
            run_cmd(f"scp {username}@{host}:{f} {processing_dir}")
        rid = conf['run_id']
        if not os.path.exists(results_json_path):
            
            with open(results_json_path, "w") as f:
                json.dump({}, f)

        local_file_paths = [f"{processing_dir}/{f.split('/')[-1]}" for f in conf['files']]
        
        run_mp(
            ftype = conf['ftype'], 
            files = local_file_paths, 
            run_id = conf['run_id'], 
            platform = conf['platform'],
            species = conf['species'],
            results_dir = processing_dir,
            threads = args.threads
        )

        if not os.path.exists(results_json_path) or os.path.getsize(results_json_path) == 0:
            file_content = ""
        else:
            with open(results_json_path, "r") as file:
                file_content = file.read().strip()
        if not os.path.exists(results_json_path) or file_content == "{}" or file_content == "":
            sys.stderr.write(f"Results JSON file {results_json_path} is empty.\n")
            errlog_path = f"{err_dir}/{rid}.errlog.txt"
            
            if os.path.exists(errlog_path):
                print("YEP")
                with open(f"{err_dir}/{rid}.errlog.txt") as file:
                    lines = file.readlines()
                    for i, line in enumerate(lines):
                        if line.startswith("## Value:"):
                            error_value = lines[i+2].strip()
                            break
                    with open(results_json_path, "w") as f:
                        print(error_value)
                        json.dump({"error": error_value}, f)
            else:
                with open(results_json_path, "w") as f:
                    json.dump({"error": "Unexpected error format"}, f)

        
        if not os.path.exists(results_txt_path):
            
            open(results_txt_path, "w").close()

        if not os.path.exists(results_bam_path):
            
            open(results_bam_path, "w").close()

        if not os.path.exists(results_bam_bai_path):
            
            open(results_bam_bai_path, "w").close()    


        created_files = {
            "results_txt": f"{processing_dir}/{rid}.results.txt",
            "results_json": f"{processing_dir}/{rid}.results.json",
            "results_bam": f"{processing_dir}/{rid}.bam"
        }

        completion_json_file = f"{rid}.completed.json"
        json.dump(created_files,open(completion_json_file,"w"))
        sys.stderr.write(f"scp {completion_json_file} {' '.join(created_files.values())}  {username}@{host}:{watch_directory}/\n")
        run_cmd(f"scp {completion_json_file} {' '.join(created_files.values())}  {username}@{host}:{watch_directory}/")


    runs_in_progress = set()

    while True:
        time.sleep(1)
        run_files = cmd_out(f"ssh {username}@{host} 'ls {watch_directory}/*run_file.json'")
        completed_files = cmd_out(f"ssh {username}@{host} 'ls {watch_directory}/*completed.json'")
        
        completed_file_basenames = set([l.strip().split("/")[-1].replace("completed.json", "") for l in completed_files])
        
        for l in run_files:
            run_file = l.strip().split("/")[-1]
            run_basename = run_file.replace("run_file.json", "")
            
            if run_basename not in completed_file_basenames and run_file not in runs_in_progress:
                runs_in_progress.add(run_file)
                process_run(run_file)

    
parser = argparse.ArgumentParser(description='add required annotations',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--remote-directory',type=str,help='Remote directory to watch for new runs',required = True)
parser.add_argument('--username',type=str,help='Username for remote server',required = True)
parser.add_argument('--host',type=str,help='Host for remote server',required = True)
parser.add_argument('--processing-dir',type=str,help='Directory to store results',required = True)
parser.add_argument('--errlog_dir',type=str,help="where are the error logs located",required=True)
parser.add_argument('--threads',type=int,help='Number of threads to use',default=1)
parser.set_defaults(func=main)
args = parser.parse_args()
args.func(args)