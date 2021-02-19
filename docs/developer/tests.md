# Testing

## Code linting

We use a combination of `flake8` and `python-black` to lint the python code.

### Install the git hook

It is recommended to install the pre-commit git-hook to automatically check your code before a commit is made.

In the top level directory run:

```bash
$ ln -s ./pre-commit.sh ./.git/hooks/pre-commit
```