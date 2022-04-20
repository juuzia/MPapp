# MPapp

## Install env
```
conda env create -f MPapp_env.yml
```

## Install malaria-profiler

## Run app
```
redis-server
sh celery.sh

cd MPapp
export FLASK_APP=MPapp
export FLASK_ENV=development
flask run --host=0.0.0.0
```