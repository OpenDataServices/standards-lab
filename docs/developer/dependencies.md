# Dependencies

We have a number of external dependencies for both the frontend and backend.

## Updating python requirements

The python requirements are defined in `requirements.in` and `requirements_dev.in` these are used to generate `requirements.txt` and `requirements_dev.txt` using `pip-compile`.


### Using pip-compile in docker

(Re)Generate the requirements files:

```
$ docker run --rm -v $(pwd):/code rhiaro/pip-tools <selected requirements.in file>
```

Upgrade the requirements:

TODO


### Using pip-compile locally

(Re)Generate the requirements files:

```
$ pip-compile <selected requirements.in file>
```

Upgrade the requirements:

```
$ pip-compile --upgrade <selected requirements.in file>
```

## Javascript dependencies

We currently use:

* VueJS
* Bootstrap
* JQuery
* [v-jsoneditor](https://github.com/yansenlei/VJsoneditor)

### v-jsoneditor

This is VueJS wrapper for jsoneditor. To build v-jsoneditor:

```
# In the top level directory with the `package-lock.json`.
$ npm install
```

The minified javascript used in `standards_lab/ui/static/v-jsoneditor/js/` is then output to
`./node_modules/v-jsoneditor/dist/`.