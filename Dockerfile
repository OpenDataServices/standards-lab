FROM python:3.9.1-buster
RUN mkdir /code
WORKDIR /code
COPY requirements_dev.txt /code/
RUN pip install -r requirements_dev.txt
COPY . /code/
CMD sh -c ' \
    cd standards_lab && \
    python manage.py runserver 0.0.0.0:8001 \
    '
EXPOSE 8001
