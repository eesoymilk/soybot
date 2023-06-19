FROM python:3-alpine3.18

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

WORKDIR /usr/src/app

RUN pip3 install --upgrade pip
RUN python3 -m venv venv
RUN source ./venv/bin/activate
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python3", "lancher.py", "-e", "docker"]
