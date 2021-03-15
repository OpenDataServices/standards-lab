# Project Files

Projects are stored in a directory that is specified by setting `ROOT_PROJECTS_DIR` in the django settings. The default is `/tmp/standards-lab`.

The value of `ROOT_PROJECTS_DIR` must be created before using Standards Lab.

The project directory includes, uploaded data, uploaded schema and the project's current settings.

## Management of files

There is no automatic management of projects. Deleting a project's directory will delete the project from Standards Lab.

Depending on your system it may be useful to use a `cron` job to periodically clear out projects that are no longer being used. This could be achieved using `find` and the `mtime` argument.
