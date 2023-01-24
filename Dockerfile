FROM python:3.9.16-buster
RUN mkdir /code
WORKDIR /
COPY requirements_dev.txt /code/
# Build our own copy of lxml using Ubuntu's libxml2/libxslt
# (don't use the prebuilt wheel)
# https://opendataservices.plan.io/issues/36790
RUN apt install libxml2-dev libxslt-dev
RUN pip install --no-binary lxml -r /code/requirements_dev.txt
COPY . /code/
WORKDIR /code/
ENV ROOT_PROJECTS_DIR=/projects_dir
ENV STATIC_ROOT=/staticfiles
RUN sh -c 'cd standards_lab && python manage.py collectstatic'
CMD sh -c ' \
    mkdir -p "$ROOT_PROJECTS_DIR" && \
    cd standards_lab && \
    gunicorn --bind 0.0.0.0:80 wsgi:application \
    '
EXPOSE 80
