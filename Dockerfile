FROM python:3.7.2-alpine3.8

COPY requirements.txt /groupme-backup/requirements.txt

RUN /sbin/apk add --no-cache su-exec \
 && /usr/local/bin/pip install --no-cache-dir --requirement /groupme-backup/requirements.txt

COPY . /groupme-backup
RUN chmod +x /groupme-backup/docker-entrypoint.sh

ENTRYPOINT ["/groupme-backup/docker-entrypoint.sh"]

ENV PYTHONUNBUFFERED 1
ENV USER_SPEC 1000:1000

LABEL maintainer=william@subtlecoolness.com \
      org.label-schema.schema-version=1.0 \
      org.label-schema.version=2.0.3
