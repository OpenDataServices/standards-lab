FROM python:3.9.1-buster
RUN mkdir /code
WORKDIR /
COPY requirements_dev.txt /code/
RUN pip install -r /code/requirements_dev.txt
COPY . /code/
WORKDIR /code/
CMD sh -c ' \
    cd standards_lab && \
    python manage.py runserver 0.0.0.0:8001 \
    '
ENV ROOT_PROJECTS_DIR=/projects_dir
EXPOSE 8001
