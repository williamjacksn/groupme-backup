FROM python:3.11.8-alpine3.19

COPY requirements.txt /groupme-backup/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /groupme-backup/requirements.txt

COPY groupme_backup.py /groupme-backup/groupme_backup.py

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/groupme-backup/groupme_backup.py"]

ENV APP_VERSION="2021.1" \
    PYTHONUNBUFFERED="1"

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.version="${APP_VERSION}"
