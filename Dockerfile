FROM python:3.8-alpine
RUN /usr/local/bin/python -m pip install --upgrade pip
WORKDIR /usr/src/app
RUN apk update \
    && apk add --no-cache openssl-dev libffi-dev build-base
#    && apk add --virtual build-deps gcc python3-dev musl-dev \
#    && apk add --no-cache mariadb-dev
COPY base_requirements.txt ./
RUN pip install --no-cache-dir -r base_requirements.txt
RUN apk del openssl-dev libffi-dev build-base
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod a+x main.py
CMD ["./main.py"]