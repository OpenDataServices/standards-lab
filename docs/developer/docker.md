# Development and the docker environment

We use docker and dokku in production, and docker-compose can be used as a local development environment.

Start everything up with `docker-compose up`. This will show you logs from all of the running containers in the console. To run it in the background, use `docker-compose up -d`. Shut it down with `docker-compose down`.

To see the logs (eg. in another console, or if you're running it in the background), run `docker-compose logs`. To see logs for a particular container, run `docker-compose logs [containter]`, eg. `docker-compose logs redis` (with the service names from the `docker-compose` file). Use the `docker-compose logs -f` to continually show the logs as the service runs.

## Updating the Dockerfile

If you make changes to either `Dockerfile` or `docker-compose.yml` you'll need to rebuild it locally to test it:

```
$ docker-compose down # (if running)
$ docker-compose build --no-cache
$ docker-compose up # (to restart)
```

## Updating the code

You'll need to rebuild the docker environment if you [add, remove, or upgrade the dependencies](dependencies.md).

Restart the containers when you edit Python code for the changes to take effect (`docker-compose down` and `docker-compose up`).

Read about [how to run the tests locally with docker](tests.md).