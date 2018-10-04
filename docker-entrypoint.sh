#!/bin/sh

USER_SPEC=${USER_SPEC:-1000}

exec /sbin/su-exec "${USER_SPEC}" /usr/local/bin/python /groupme_backup.py
