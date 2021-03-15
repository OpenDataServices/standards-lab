# Process Management

Standards Lab requires 3 main processes to be running, the Web Server, the queue worker and the in-memory storage server.

## Webserver

Using the docker based deployment a webserver process is provided using [gunicorn](https://docs.gunicorn.org/).

The webserver process runs the [django web framework](https://docs.djangoproject.com/en/3.1/howto/deployment/) and serves static files such as javascript and css.

## Queue worker process

To test and process data django-rq is used to start, manage and monitor the processes.

The worker process uses [django-rq](https://github.com/rq/django-rq) to create processes when requested by the user, an example of a process would be the CoVE process.

Restarting this process may cause any in-progress processes to be terminated. If this process is not running the Test functionality will not work.

This process requires a working Redis server.

## In-memory storage server

[Redis](https://redis.io/commands) is used as the in-memory storage server.

Redis holds results from processes, is used by (django) RQ and as a cache for the webserver.

Restarting Redis may clear any in progress processes and results.