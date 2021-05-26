# Hosting on Dokku

Standards Lab is designed to be hosted on Dokku.

To set up an app, run these commands on the Dokku server:

    # Set an app name
    export APP_NAME = "standards-lab"
    # Create the app
    dokku apps:create $APP_NAME
    # Set up the domain you want to use (you may need to use the dokku domains command here too)
    dokku config:set $APP_NAME ALLOWED_HOSTS=xxxxx
    # Create a Redis store, and link it to the app
    dokku redis:create $APP_NAME
    dokku redis:link $APP_NAME $APP_NAME
    # Setup file storage
    dokku storage:mount $APP_NAME /var/lib/dokku/data/storage/$APP_NAME/projects_dir:/projects_dir
    # Configure the ports the webserver uses
    dokku proxy:ports-add $APP_NAME http:80:80
    # Set up the number of web servers and workers - change if needed; but at least 1 of each
    dokku ps:scale $APP_NAME web=1 worker=1
    # Set option - this is needed so that the about page can display what version of the software is deployed
    dokku git:set $APP_NAME keep-git-dir true

Now deploy the repository to Dokku in the usual way (a `git push` or `dokku git:sync` command).

Optionally, add an SSL certificate by one of the usual ways. For example: https://github.com/dokku/dokku-letsencrypt
