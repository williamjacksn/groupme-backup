FROM python:3.7.3-alpine3.9

COPY requirements.txt /groupme-backup/requirements.txt

RUN /sbin/apk add --no-cache su-exec \
 && /usr/local/bin/pip install --no-cache-dir --requirement /groupme-backup/requirements.txt

COPY . /groupme-backup
RUN chmod +x /groupme-backup/docker-entrypoint.sh

ENTRYPOINT ["/groupme-backup/docker-entrypoint.sh"]

ENV PYTHONUNBUFFERED="1" \
    USER_SPEC="1000:1000"

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.version=2.0.5
