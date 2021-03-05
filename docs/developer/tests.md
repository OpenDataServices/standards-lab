# Testing

## Code linting

We use a combination of `flake8` and `python-black` to lint the python code.

### Install the git hook

It is recommended to install the pre-commit git-hook to automatically check your code before a commit is made.

In the top level directory run:

```bash
$ ln -s ./pre-commit.sh ./.git/hooks/pre-commit
```

## Running tests locally

Tests for the API, UI and processor are in their respective directories.

### With docker

To run the tests with a docker development setup:

```bash
$ docker-compose run standards-lab-worker standards_lab/manage.py test standards_lab
```

### Locally

To run the tests in your local virtual environment:

```bash
$ cd standards_lab
$ python manage.py test
```
