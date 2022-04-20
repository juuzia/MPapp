import os
import uuid
import re

from flask import (
    Blueprint, flash, request, redirect, render_template, url_for, current_app, send_file)
from flask import current_app as app

from werkzeug.utils import secure_filename # to secure file
from .worker import run_mp_fastq, run_mp_bam, get_status

bp = Blueprint('main', __name__)



@bp.route('/')
def index():
    return render_template("pages/index.html")

@bp.route('/analysis', methods=["GET", "POST"])
def analysis():
    if request.method == "POST":
        if request.files:
            error=None
            run_id = str(uuid.uuid4())
            if "fastq_submit" in request.form:
                fq1 = request.files["file1"]
                fq2 = request.files["file2"]

                if (fq1.filename == "") & (fq2.filename == ""):
                    error="No files selected. Please specify FASTQ or BAM/CRAM files"
                if not(check_file_extension(fq1.filename) & check_file_extension(fq2.filename)):
                   error="This file extension is not allowed."

                if error:
                    flash(error, "danger") #TODO does not display it as redirect happens to quickly
                else:
                    process = run_fastq_pipeline(fq1, fq2, run_id)
                    while process.status != 'SUCCESS': # process.ready = True/False
                        return redirect(url_for('main.pending', run_id=run_id))
                    else:
                        return redirect(url_for('main.result_id', run_id=run_id))
            if "bam_submit" in request.form:
                bam = request.files["bam"]
                
                if bam.filename == "":
                    error="No filename"
                if not(check_file_extension(bam.filename, bam=True)):
                    error="This file extension is not allowed."
                
                if error:
                    flash(error, "error") #TODO does not display it as redirect happens to quickly
                else:
                    process = run_bam_pipeline(bam, run_id)
                    while process.status != 'SUCCESS':
                        return redirect(url_for('main.pending', run_id=run_id))
                    else:
                        return redirect(url_for('main.result_id', run_id=run_id))

    return render_template("pages/analysis.html")

def check_file_extension(filename, bam=False):
    pattern = "\.fastq?.[A-Za-z]*$|\.fq?.[A-Za-z]*$"
    if bam:
        pattern = "\.bam$"
   
    ext = filename.strip().lower()

    # Check pattern
    if re.search(pattern, ext):
        return True
    else:
        return False

def run_fastq_pipeline(fq1, fq2, run_id):
    f1_path = secure_filename(fq1.filename)
    f2_path = secure_filename(fq2.filename)

    fq1.save(os.path.join(app.config["UPLOAD_FOLDER"], f1_path))
    fq2.save(os.path.join(app.config["UPLOAD_FOLDER"], f2_path))

    fpath1 = "/%s/%s" % (app.config["UPLOAD_FOLDER"], f1_path)
    fpath2 = "/%s/%s" % (app.config["UPLOAD_FOLDER"], f2_path)

    with open("%s/%s.log" % (app.config["RESULTS_DIR"], run_id), "w") as O:
        O.write("Starting job:\n")
        O.write("F1: %s\n" % fpath1)
        O.write("F2: %s\n" % fpath2)
    x = run_mp_fastq.delay(fpath1, fpath2, run_id, app.config["RESULTS_DIR"])
    return x

@bp.route('/result/<uuid:run_id>/pending')
def pending(run_id):
    log_file = "%s/%s.log" % (app.config["RESULTS_DIR"], run_id)
    if not os.path.isfile(log_file):
        flash("Error! Result with ID:%s doesn't exist" % run_id, "danger")
        return render_template('pages/result.html')
    else:
        flash("Files uploaded", "success")
        flash("Analysis in progress. Check in later", "info")
        return render_template('pages/pending.html', run_id=run_id)

@bp.route('/result/<uuid:run_id>')
def result_id(run_id):
    log_file = "%s/%s.log" % (app.config["RESULTS_DIR"], run_id)
    if not os.path.isfile(log_file):
        flash("Error! Result with ID:%s doesn't exist" % run_id, "danger")
        return render_template('pages/result.html')
    result_file = "%s/%s.results.txt" % (app.config["RESULTS_DIR"], run_id)
    if not os.path.isfile(result_file):
        return render_template('pages/pending', run_id=run_id)
    else:
        results = open(result_file).read()
        return render_template('pages/result_id.html', run_id=run_id, results = results)

@bp.route('/result/<uuid:run_id>/download', methods=['GET', 'POST'])
def download(run_id):
        result_file = "%s/%s.results.txt" % (app.config["RESULTS_DIR"], run_id)
        return send_file(result_file, as_attachment=True)

@bp.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == "POST":
        if "result_submit" in request.form:
            #TODO # trim it  
            run_id = request.form["result_id"].strip()
            log_file = "%s/%s.log" % (app.config["RESULTS_DIR"], run_id)
            if not os.path.isfile(log_file):
                flash("Error! Result with ID:%s doesn't exist" % run_id, "danger")
                return render_template('pages/result.html')
            result_file = "%s/%s.results.txt" % (app.config["RESULTS_DIR"], run_id)
            if not os.path.isfile(result_file):
                return redirect(url_for('main.pending', run_id=run_id))
            else:
                results = open(result_file).read()
                return redirect(url_for('main.result_id', run_id=run_id))
    return render_template("pages/result.html")

def run_bam_pipeline(bam, run_id):
    bam_path = secure_filename(bam.filename)

    bam.save(os.path.join(app.config["UPLOAD_FOLDER"], bam_path))
    fpath = "/%s/%s" % (app.config["UPLOAD_FOLDER"], bam_path)

    with open("%s/%s.log" % (app.config["RESULTS_DIR"], run_id), "w") as O:
        O.write("Starting job:\n")
        O.write("F1: %s\n" % fpath)
    x = run_mp_bam.delay(fpath, run_id, app.config["RESULTS_DIR"])
    return x
