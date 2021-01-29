FROM python:3.9.1-buster
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
CMD sh -c ' \
    mkdir /tmp/standards-lab/ && \
    cd standards_lab && \
    python manage.py runserver 0.0.0.0:8001 \
    '
EXPOSE 8001
