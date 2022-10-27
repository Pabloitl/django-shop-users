FROM python:3.10

ENV PYTHONUNBUFFERED 1
WORKDIR /app/

RUN pip3 install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy
