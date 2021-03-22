# Process Management

Standards Lab requires 3 main processes to be running, the webserver, the queue worker and the in-memory storage server.

## Webserver

Using the Docker based deployment a webserver process is provided using [gunicorn](https://docs.gunicorn.org/).

The webserver process runs the [Django web framework](https://docs.djangoproject.com/en/3.1/howto/deployment/) and serves static files such as JavaScript and CSS.

## Queue worker process

[django-rq](https://github.com/rq/django-rq) is used to start, manage and monitor the processes that test and process data.

The worker process uses [django-rq](https://github.com/rq/django-rq) to create processes when requested by the user. An example of a process is the CoVE process.

Restarting this process may cause any in-progress processes to be terminated. If this process is not running the Test functionality will not work.

This process requires a working Redis server.

## In-memory storage server

[Redis](https://redis.io/commands) is used as the in-memory storage server.

Redis holds results from processes, is used by (django) RQ and as a cache for the webserver.

Restarting Redis may clear any in progress processes and results.
