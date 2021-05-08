# Separate base image so that we can use it to update the Pipfile.lock and requirements.txt file
FROM python:3.9.1-slim AS base
ENV FLASK_APP=aspen.main
EXPOSE 3000
RUN pip install --no-cache-dir pipenv
WORKDIR /usr/src/app
COPY requirements.txt .
COPY Pipfile* ./
COPY third-party ./third-party/
ENV PIPENV_PYTHON=/usr/src/app/
COPY setup.py .
RUN pipenv install --dev --system --verbose && pipenv --clear
RUN apt-get update && apt-get install make
COPY . .
ENTRYPOINT ["./entrypoint.sh"]
