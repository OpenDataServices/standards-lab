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

### Locally

To run the tests in your local virtual environment:

```bash
$ cd standards_lab
$ python manage.py test
```

### With Docker Compose

[See the Docker page](docker.md)
