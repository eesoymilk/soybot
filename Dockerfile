FROM python:3-alpine3.18

WORKDIR /usr/src/app

RUN pip3 install --upgrade pip
RUN python3 -m venv venv
RUN source ./venv/bin/activate

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD ["python3", "lancher.py", "-e", "docker"]
