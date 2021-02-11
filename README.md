# Open Standards Lab
Open Standards Lab. A web tool for users and creators of Open Standards.

# Installing and running Open Standards Lab

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

Install Docker and Docker Compose.

Then

```
docker-compose build
docker-compose up
```

[See developer docs for more information](docs/developer/)