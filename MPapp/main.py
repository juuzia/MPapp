from collections import defaultdict, namedtuple
import os
from uuid import uuid4
import re

from flask import (
    Blueprint, flash, request, redirect, render_template, url_for, current_app, send_file, make_response, Response)
from flask import current_app as app
from glob import glob
from werkzeug.utils import secure_filename # to secure file
from .worker import run_mp, get_status
import io
import csv
bp = Blueprint('main', __name__)

def get_upload_dir(upload_id):
    return os.path.join(app.config["UPLOAD_FOLDER"],upload_id)

@bp.route('/')
def index():
    return render_template("pages/index.html")

@bp.route('/analysis', methods=["GET", "POST"])
def analysis():
    random_id = str(uuid4())
    if request.method == "POST":
        runs = []
        upload_id = request.form['submit_button']
        upload_dir = get_upload_dir(upload_id)
        new_upload_id = str(uuid4())
        new_upload_dir = get_upload_dir(new_upload_id)
        os.rename(upload_dir,new_upload_dir)
        for f in get_files_in_dir(new_upload_dir):
            run_id = str(uuid4())
            with open("%s/%s.log" % (app.config["RESULTS_DIR"], run_id), "w") as O:
                O.write("Starting job: %s\n" % run_id)
            run_mp.delay(f.type, f.files, run_id, app.config["RESULTS_DIR"])
            runs.append({"id":run_id,"files":f.files})
        with io.StringIO() as O:
            writer = csv.DictWriter(O,list(runs[0]))
            writer.writeheader()
            writer.writerows(runs)
            csv_text = O.getvalue()
        return Response(csv_text,mimetype="text/csv",headers={"Content-disposition": "attachment; filename=run-ids.csv"})
        
    return render_template("pages/analysis.html",random_id=random_id)

file_patterns = {
    "fasta": "\.fasta$|\.fa$",
    "fastq": "\.fastq.[A-Za-z]*$|\.fq.[A-Za-z]*$",
    "bam": "\.bam$",
    "cram": "\.cram$"
}

def get_filetype(filename):
    for key,pattern in file_patterns.items():
        if re.search(pattern,filename.strip().lower()):
            print(key)
            return key
    return None

def get_files_in_dir(upload_dir):
    file_list = glob("%s/*" % upload_dir)
    File = namedtuple("File", "files type")
    files = []
    fastqs = []
    for f in file_list:
        ftype = get_filetype(f)
        if ftype=="fastq":
            fastqs.append(f)
        else:
            files.append(File((f,),ftype))

    pattern = "(.*)(_R?[12])(\.fastq.[A-Za-z]*$)|(.*)(_R?[12])(\.fq.[A-Za-z]*$)"
    
    while len(fastqs)>0:
        f = fastqs.pop()
        r = re.search(pattern,f)
        if r:
            if r.group(2)=="_1":
                potential_pair = r.group(1)+"_2"+r.group(3)
            else:
                potential_pair = r.group(1)+"_R2"+r.group(3)

            if potential_pair in fastqs:
                pair = fastqs.pop(fastqs.index(potential_pair))
                files.append(File((f,pair),"fastq"))
            else:
                files.append(File((f,),"fastq"))
        else:
            files.append(File((f,),"fastq"))

    return(files)

def is_legal_filetype(filename):
    if get_filetype(filename):
        return True
    else:
        return False

@bp.route('/result/<uuid:run_id>')
def result_id(run_id):
    log_file = "%s/%s.log" % (app.config["RESULTS_DIR"], run_id)
    if not os.path.isfile(log_file):
        flash("Error! Result with ID:%s doesn't exist" % run_id, "danger")
        return render_template('pages/result.html')
    result_file = "%s/%s.results.txt" % (app.config["RESULTS_DIR"], run_id)
    if not os.path.isfile(result_file):
        status = "Processing"
        results = None
        flash("Analysis in progress...", "info")
        flash("Wait or copy Result ID and check later.", "info")
        return render_template('pages/result_id.html', run_id=run_id, results = results, status=status)
    else:
        status = "OK"
        results = open(result_file).read()
        return render_template('pages/result_id.html', run_id=run_id, results = results, status=status)

@bp.route('/result/<uuid:run_id>/download', methods=['GET', 'POST'])
def download(run_id):
        result_file = "%s/%s.results.txt" % (app.config["RESULTS_DIR"], run_id)
        return send_file(result_file, as_attachment=True)

@bp.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == "POST":
        if "result_submit" in request.form:
            run_id = request.form["result_id"].strip()
            return redirect(url_for('main.result_id', run_id=run_id))
    return render_template("pages/result.html")



@bp.route('/file_upload/<uuid:upload_id>',methods=('GET','POST'))
def file_upload(upload_id):

    upload_id = str(upload_id)
    file = request.files['file']
    if not is_legal_filetype(file.filename):
        return make_response(('Unknown file type', 400))

    upload_dir = os.path.join(app.config["UPLOAD_FOLDER"],upload_id)
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)
    save_path = os.path.join(upload_dir, file.filename)
    current_chunk = int(request.form['dzchunkindex'])
    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return make_response(('File already exists', 400))
    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        # log.exception will include the traceback so we can see what's wrong 
        # log.exception('Could not write to file')
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))
    total_chunks = int(request.form['dztotalchunkcount'])
    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            return make_response(('Size mismatch', 500))
        else:
            print(f'File {file.filename} has been uploaded successfully from session {upload_id} to {save_path}')
    else:
        print(f'Chunk {current_chunk + 1} of {total_chunks} for file {file.filename} complete')
    return make_response(("Chunk upload successful", 200))