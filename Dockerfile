FROM python:3.9.1-buster
RUN mkdir /code
WORKDIR /
COPY requirements_dev.txt /code/
RUN pip install -r /code/requirements_dev.txt
COPY . /code/
WORKDIR /code/
ENV ROOT_PROJECTS_DIR=/projects_dir
ENV STATIC_ROOT=/staticfiles
RUN sh -c 'cd standards_lab && python manage.py collectstatic'
CMD sh -c ' \
    mkdir -p "$ROOT_PROJECTS_DIR" && \
    cd standards_lab && \
    gunicorn --bind 0.0.0.0:80 wsgi:application --reload \
    '
EXPOSE 80
