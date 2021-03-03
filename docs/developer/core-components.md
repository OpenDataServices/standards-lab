# Core components

## Main

The main application is the django framework which loads the three django applications which make up standards lab.
* ui
* api
* processor

The django framework is configured using:

* `settings/<settings file>`
* `urls.py`
* `wsgi.py`
* `manage.py`

## UI

The UI application is further separated into two applications depending on responsibility.

The Django UI application is responsible for:

* URL routing
* Http Requests
* Templates
* Views
* Common data templates' context

The VueJS application is responsible for:

* Interactivity within the web page
* Rendering and two way bindings of in-page VueJS templates with data from the API
* Sending and receiving data from the API

## API

The API provides endpoints primarily for the VueJS application. All responses are `JSON` format.

`/api/`
* `project/<project-name>`
  * GET: returns project configuration
  * POST: (`JSON`) updates or creates the project configuration (edit mode only)

* `project/<project-name>/upload`
  * POST: Upload data to the project. (`FormData`) `FILE` required properties `uploadType` values `"schema"` or `"data"` for the different upload types.

* `project/<project-name>/download/<file-name>`
  * GET: Returns project file. Optional property `attach=true` determines if the file should be sent to the browser as an attachment or as data. Default not present.

* `project/<project-name>/process`
  * GET: Returns the status(es) and results of any Processor running for specified project
  * POST: (`JSON`) required properties `action` value `"start"`, `processName` value `"<name-of-processor>"`

## Processor

The processor is responsible for starting, defining and communicating with processing jobs. Each processor implements a `start` function and a `monitor` function.

When you run Standards Lab using docker-compose, the redis queue data is persisted in the `_build/redis-data/` directory.

## Utils

Utility functions that are common to all of the django applications.