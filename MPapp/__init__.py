import os
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_url_path='/malaria-profiler/static', static_folder='static')
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER="/tmp",
        THREADS=4,
        RUN_SUBMISSION="remote",
        APP_ROOT=os.path.dirname(os.path.abspath(__file__)),
        RESULTS_DIR=os.path.dirname(os.path.abspath(__file__)) + "/static/results"
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import main
    app.register_blueprint(main.bp)

    return app
