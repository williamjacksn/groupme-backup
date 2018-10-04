FROM python:3.7.0-alpine3.8

LABEL version="2.0.0"

COPY requirements.txt /requirements.txt

RUN /sbin/apk add --no-cache su-exec \
 && /usr/local/bin/pip install --no-cache-dir --upgrade setuptools wheel \
 && /usr/local/bin/pip install --no-cache-dir --requirement /requirements.txt

COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY groupme_backup.py /groupme_backup.py

ENV PYTHONUNBUFFERED 1
ENV USER_SPEC 1000:1000

ENTRYPOINT ["/docker-entrypoint.sh"]
