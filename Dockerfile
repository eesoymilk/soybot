FROM python:3-alpine3.18

WORKDIR /usr/src/app

RUN python3 -m venv vene
RUN source venv/bin/activate
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD ["python3", "lancher.py", "-e", "docker"]
