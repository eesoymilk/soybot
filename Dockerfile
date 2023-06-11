FROM python:3-alpine3.18

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .
CMD ["python3", "lancher.py", "-m", "docker"]
