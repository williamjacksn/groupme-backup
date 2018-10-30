FROM python:3.7.1-alpine3.8

COPY requirements.txt /requirements.txt

RUN /sbin/apk add --no-cache su-exec \
 && /usr/local/bin/pip install --no-cache-dir --requirement /requirements.txt

COPY groupme_backup.py /groupme_backup.py
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONUNBUFFERED 1
ENV USER_SPEC 1000:1000

ENTRYPOINT ["/docker-entrypoint.sh"]

LABEL maintainer=william@subtlecoolness.com \
      org.label-schema.schema-version=1.0 \
      org.label-schema.version=2.0.3
