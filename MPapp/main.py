from collections import defaultdict, namedtuple
import os
from uuid import uuid4
import re
import time

from flask import (
    Blueprint, flash, request, redirect, render_template, url_for, current_app, send_file, make_response, Response)
from flask import current_app as app
from glob import glob
from werkzeug.utils import secure_filename # to secure file
from .worker import run_mp, get_status, remote_profile
import io
import json
import csv
import pathogenprofiler as pp

bp = Blueprint('main', __name__)

def get_upload_dir(upload_id):
    return os.path.join(app.config["UPLOAD_FOLDER"],upload_id)

@bp.route('/')
def index():
    return render_template("pages/index.html")

@bp.route('/analysis', methods=["GET", "POST"])
def analysis():
    species_list = [
        ('falciparum', 'Plasmodium falciparum'),
        ('vivax_simium', 'Plasmodium vivax'),
        ('knowlesi', 'Plasmodium lnowlesi'),
        ('malariae_brasilianum', 'Plasmodium malariae'),
        ('ovale', 'Plasmodium ovale'),
        ('autodetect', 'Autodetect')
    ]
    random_id = str(uuid4())
    if request.method == "POST":
        #if  == "illumina":
        platform = request.form["radio_platform"]
        species = request.form["species"]
        print(species)

        runs = []
        upload_id = request.form['submit_button']
        upload_dir = get_upload_dir(upload_id)
        if not os.path.isdir(upload_dir):
            flash("No new files uploaded","danger")
            return render_template("pages/analysis.html", random_id=random_id, species=species_list)

        new_upload_id = str(uuid4())
        new_upload_dir = get_upload_dir(new_upload_id)
        os.rename(upload_dir,new_upload_dir)

        for f in get_files_in_dir(new_upload_dir):
            run_id = str(uuid4())
            with open("%s/%s.log" % (app.config["RESULTS_DIR"], run_id), "w") as O:
                O.write("Starting job: %s\n" % run_id)
            if app.config["RUN_SUBMISSION"]=="local":
                run_mp.delay(f.type, f.files, run_id, app.config["RESULTS_DIR"], platform,species=species,threads=app.config["THREADS"])
            elif app.config["RUN_SUBMISSION"]=="remote":
                remote_profile.delay(f.type, f.files, run_id, app.config["RESULTS_DIR"], platform,species=species)
            else:
                raise Exception("Unknown RUN_SUBMISSION type: %s" % app.config["RUN_SUBMISSION"])
            runs.append({"id":run_id, "files":f.files})
        analysis_id = str(uuid4())
        with open("%s/%s.json" % (app.config["RESULTS_DIR"],analysis_id), "w") as O:
            json.dump(runs,O)
        return redirect(url_for("main.analysis_runs_id", analysis_id=analysis_id))
        # with io.StringIO() as O:
        #     writer = csv.DictWriter(O,list(runs[0]))
        #     writer.writeheader()
        #     writer.writerows(runs)
        #     csv_text = O.getvalue()
        # return Response(csv_text,mimetype="text/csv",headers={"Content-disposition": "attachment; filename=run-ids.csv"})
    
    return render_template("pages/analysis.html", random_id=random_id,species = species_list)

file_patterns = {
    "fasta": "\.fasta$|\.fa$",
    "fastq": "\.fastq.[A-Za-z]*$|\.fq.[A-Za-z]*$",
    "bam": "\.bam$",
    "cram": "\.cram$"
}

@bp.route('/run_result/<uuid:analysis_id>')
def analysis_runs_id(analysis_id):
    data = json.load(open("%s/%s.json" % (app.config["RESULTS_DIR"], analysis_id)))
    for d in data:
        d["link"] = '<a href="' + url_for("main.result_id", run_id=d["id"]) + '">' + d["id"] + '</a>'
        d["files"] = ", ".join([x.split("/")[-1] for x in d["files"]])
    return render_template('/pages/analysis_id.html', runs = data)

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

    fastqs = sorted(fastqs)
    while len(fastqs)>0:
        f = fastqs.pop(0)
        r = re.search(pattern,f)
        if r:
            if r.group(2)=="_1":
                potential_pair = r.group(1)+"_2"+r.group(3)
            else:
                potential_pair = r.group(1)+"_R2"+r.group(3)

            print(f"Looking for {potential_pair} in {str(fastqs)}: {potential_pair in fastqs}")
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

def get_conf(results):
    db_name = results['resistance_db_version']['name']
    conf = pp.get_db('malaria_profiler',db_name)
    return conf

def parse_result_summary(json_file):
    geoclass, drugs, var_drug, variants, gene_coverage, missing = None, None, None, None, None, None

    with open(json_file) as json_file:
        json_results = json.load(json_file, parse_float=lambda x: round(float(x), 2))

    conf = get_conf(json_results)

    info = ([{"id" : json_results['id'], "date": time.ctime()}],
            {"id": "Identifier",
             "date": "Date"})

    if len(json_results['species']['prediction'])==0:
        json_results['species']['prediction'] = [{"species": json_results['resistance_db_version']['name'], "mean": 0, "std": 0}]

    species = (
        json_results['species']['prediction_info'],
        {
            "species": "Species",
            "mean": "Mean kmer coverage",
            "std": "Standard dev"
        }
    )

    analysis = (json_results['pipeline_software'],
                {'Analysis': 'Analysis',
                 'Program': 'Program'})

    if conf:
        if "drugs" in conf:
            json_results = pp.get_summary(json_results, conf, columns = None)

        if "geoclassification" in json_results:
            converted = [{"region": l.replace("_", " ")} for l in json_results['geoclassification']]
            geoclass = (converted,
                        {"region": "Region"})

        if "drugs" in conf:
            json_results['drug_table'] = [[y for y in json_results['drug_table'] if y["Drug"].upper()==d.upper()][0] for d in conf['drugs']]
            drugs = (json_results['drug_table'],
                    {"Drug": "Drug",
                     "Genotypic Resistance": "Genotypic Resistance",
                     "Mutations": "Mutations"})

        if "dr_variants" in json_results: #TODO is this condition okay
            for var in json_results['dr_variants']:
                var['drug'] = ", ".join([d["drug"] for d in var['drugs']])
            var_drug = (json_results['dr_variants'],
                        {"chrom": "Chromosome",
                        "genome_pos": "Genome Position",
                        "locus_tag": "Locus Tag",
                        "gene": "Gene Name",
                        "change": "Change",
                        "freq": "Estimated fraction",
                        "drugs.drug": "Drug"})

        if "other_variants" in json_results:
            variants = (json_results['other_variants'],
                        {"chrom": "Chromosome:",
                        "genome_pos": "Genome Position",
                        "locus_tag": "Locus Tag",
                        "gene": "Gene Name",
                        "change": "Change",
                        "freq": "Estimated fraction"})

        if "gene_coverage" in json_results['qc']:
            gene_coverage = (json_results['qc']['gene_coverage'],
                            {"gene": "Gene",
                             "locus_tag": "Locus tag",
                             "cutoff": "Cutoff",
                             "fraction": "Fraction"})

        if "missing_positions" in json_results['qc']:
            missing = (json_results['qc']['missing_positions'],
                      {"gene": "Gene",
                       "locus_tag": "Locus tag",
                       "position": "Position",
                       "variants": "Variants",
                       "drugs": "Drugs"})
        if "qc_fail_variants" in json_results:
            fail_variants = (json_results['qc_fail_variants'],
                        {"chrom": "Chromosome:",
                        "genome_pos": "Genome Position",
                        "locus_tag": "Locus Tag",
                        "gene": "Gene Name",
                        "change": "Change",
                        "freq": "Estimated fraction"})

    tables = {
        "General information" : info,
        "Species" : species,
        "Analysis" : analysis,
        "Geoclassification": geoclass,
        "Resistance report": drugs,
        "Resistance variants report": var_drug,
        "Other variants": variants,
        "QC failed variants": fail_variants,
        "Coverage report": gene_coverage,
        "Missing positions report": missing
        }

    return tables

@bp.route('/result/<uuid:run_id>')
def result_id(run_id):
    log_file = "%s/%s.log" % (app.config["RESULTS_DIR"], run_id)
    if not os.path.isfile(log_file):
        flash("Error! Result with ID:%s doesn't exist" % run_id, "danger")
        return render_template('pages/result.html')
    result_file = "%s/%s.results.txt" % (app.config["RESULTS_DIR"], run_id)
    json_file = "%s/%s.results.json" % (app.config["RESULTS_DIR"], run_id)

    if not os.path.isfile(result_file):
        status = "Processing"
        results = None
        tables = None
        refresh_page = True
        flash("Analysis in progress...", "info")
        flash("Wait or copy Result ID and check later.", "info")
        return render_template('pages/result_id.html', run_id=run_id, results = results, status=status, tables=tables, refresh_page=refresh_page)
    else:
        status = "OK"
        results = open(result_file).read()
        tables = parse_result_summary(json_file)
        return render_template('pages/result_id.html', run_id=run_id, results = results, status=status, tables=tables)

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