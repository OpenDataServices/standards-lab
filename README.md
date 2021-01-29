# Open Standards Lab
Open Standards Lab. A web tool for users and creators of Open Standards.


# Setting up and running Open Standards Lab

## Developing standards-lab code
Installing standards lab to develop the standards-lab code
### Local system

Install:

```
# Install system dependencies
$ apt install redis python3-virtualenv

# Create python virtual environment
$ virtualenv --python python3 .ve

# Activate python virtual environment
$ source ./.ve/bin/activate

# Install python dependencies
$ pip install -r requirements.txt
$ pip install -r requirements_dev.txt
```

Run development webserver:

```
$ manage.py runserver
```


### Local using docker containers

TODO

### Python
- Before committing python code make sure to run python-black via `$ black`
- Style:
```python

variable_names = "things"

class ClassNames(object):
    pass

def function_names():
    return 1
```

### HTML
- Indent with 2 spaces
- Style:
```html
<div>
  <p>Hi</p>
</div>
```

### JS
- Indent with 2 spaces
- variables and function names camelCase
- Style:
```js
function abcdAlpha(param){

}

let obj = {
  propertyA: 1,
  propertyB: 2
}
```