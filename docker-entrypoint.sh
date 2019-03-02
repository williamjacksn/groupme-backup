#!/bin/sh

USER_SPEC="${USER_SPEC:-1000}"
DATABASE="${DATABASE-/database.db}"

chown ${USER_SPEC} "${DATABASE}"
exec /sbin/su-exec "${USER_SPEC}" /usr/local/bin/python /groupme-backup/groupme_backup.py
