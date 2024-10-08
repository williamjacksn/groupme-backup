FROM python:3.13-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python

USER python
RUN /usr/local/bin/python -m venv /home/python/venv

COPY --chown=python:python requirements.txt /home/python/groupme-backup/requirements.txt
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/groupme-backup/requirements.txt

ENV PATH="/home/python/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

ENTRYPOINT ["/home/python/venv/bin/python", "/home/python/groupme-backup/groupme_backup.py"]

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.source="https://github.com/williamjacksn/groupme-backup"

COPY --chown=python:python groupme_backup.py /home/python/groupme-backup/groupme_backup.py
