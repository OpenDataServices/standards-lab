# Open Standards Lab
Open Standards Lab. A web tool for users and creators of Open Standards.

# Installing and running Open Standards Lab

## Developing standards-lab code
Installing standards lab to develop the standards-lab code
### Local system

#### Install:

```
# Install system dependencies
$ apt install redis python3-virtualenv # or whatever you system package manger uses

# Create python virtual environment
$ virtualenv --python python3 .ve

# Activate python virtual environment
$ source ./.ve/bin/activate

# Install python dependencies
$ pip install -r requirements.txt
$ pip install -r requirements_dev.txt
```

#### Running:

Make sure redis is running:
```
 $ sudo service redis start
```
Run development webserver process:

```
$ manage.py runserver
```

Run the queue runner process:
```
$ manage.py rqworker default
```


### Local using docker containers

Install Docker and Docker Compose.

Then

```
docker-compose build
docker-compose up
```

Visit `localhost:8001` in a browser.

[See developer docs for more information](docs/developer/)