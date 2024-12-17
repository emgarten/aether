from invoke import task


@task
def lint(c):
    """
    Format and lint
    """

    c.run("isort src")
    c.run("black src")
    c.run("flake8 src")