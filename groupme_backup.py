import datetime
import decimal
import json
import logging
import os
import pathlib
import sys
from typing import Optional

import fort
import httpx

__version__ = "2024.1"


class Database(fort.SQLiteDatabase):
    def add_version(self, version: int) -> None:
        sql = """
            insert into schema_versions (schema_version, migration_date)
            values (:version, :timestamp)
        """
        params = {
            "version": version,
            "timestamp": datetime.datetime.now(tz=datetime.UTC),
        }
        self.u(sql, params)

    def migrate(self) -> None:
        if self.version < 1:
            self.log.debug("Migrating to version 1")
            sql = """
                create table emoji (
                    message_id integer,
                    placeholder text,
                    pack_id integer,
                    offset integer
                )
            """
            self.u(sql)
            sql = """
                create table files (
                    message_id integer,
                    file_id text
                )
            """
            self.u(sql)
            sql = """
                create table images (
                    message_id integer,
                    url text
                )
            """
            self.u(sql)
            sql = """
                create table mentions (
                    message_id integer,
                    user_id integer,
                    location integer,
                    length integer
                )
            """
            self.u(sql)
            sql = """
                create table messages (
                    avatar_url text,
                    created_at timestamp,
                    id integer primary key,
                    name text,
                    sender_id text,
                    sender_type text,
                    source_guid text,
                    system bool,
                    message_text text,
                    user_id text
                )
            """
            self.u(sql)
            sql = """
                create table videos (
                    message_id integer,
                    preview_url text,
                    url text
                )
            """
            self.u(sql)
            sql = """
                create table schema_versions (
                    schema_version integer,
                    migration_date timestamp
                )
            """
            self.u(sql)
            self.add_version(1)
        if self.version < 2:
            self.log.debug("Migrating to version 2")
            sql = """
                create table autokicked_members (
                    message_id integer,
                    user_id text
                )
            """
            self.u(sql)
            sql = """
                create table events (
                    message_id integer,
                    event_id text,
                    view text
                )
            """
            self.u(sql)
            sql = """
                create table locations (
                    message_id integer,
                    lat decimal,
                    lng decimal,
                    name text
                )
            """
            self.u(sql)
            self.add_version(2)

    @property
    def version(self) -> int:
        sql = "select 1 from sqlite_master where type = :type and name = :name"
        params = {"type": "table", "name": "schema_versions"}
        tbl = self.q_one(sql, params)
        if tbl is None:
            return 0
        return self.q_val("select max(schema_version) from schema_versions")


class Message:
    def __init__(self, db: Database) -> None:
        self._db = db
        self.avatar_url: str | None = None
        self.created_at: datetime.datetime | None = None
        self.id: int | None = None
        self.name: str | None = None
        self.sender_id: str | None = None
        self.sender_type: str | None = None
        self.source_guid: str | None = None
        self.system: bool | None = None
        self.message_text: str | None = None
        self.user_id: str | None = None

    def add_autokicked_member(self, user_id: str) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = """
            select 1
            from autokicked_members
            where message_id = :message_id and user_id = :user_id
        """
        params = {"message_id": self.id, "user_id": user_id}
        row = self._db.q_one(sql, params)
        if row is None:
            sql = """
                insert into autokicked_members (message_id, user_id)
                values (:message_id, :user_id)
            """
            self._db.u(sql, params)

    def add_emoji(self, placeholder: str, pack_id: int, offset: int) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = """
            select 1 from emoji
            where message_id = :message_id
            and placeholder = :placeholder and pack_id = :pack_id and offset = :offset
        """
        params = {
            "message_id": self.id,
            "placeholder": placeholder,
            "pack_id": pack_id,
            "offset": offset,
        }
        row = self._db.q_one(sql, params)
        if row is None:
            sql = """
                insert into emoji (message_id, placeholder, pack_id, offset)
                values (:message_id, :placeholder, :pack_id, :offset)
            """
            self._db.u(sql, params)

    def add_event(self, event_id: str, view: str) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = """
            select 1 from events
            where message_id = :message_id and event_id = :event_id and view = :view
        """
        params = {"message_id": self.id, "event_id": event_id, "view": view}
        row = self._db.q_one(sql, params)
        if row is None:
            sql = """
                insert into events (message_id, event_id, view)
                values (:message_id, :event_id, :view)
            """
            self._db.u(sql, params)

    def add_file(self, file_id: str) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = (
            "select 1 from files where message_id = :message_id and file_id = :file_id"
        )
        params = {"message_id": self.id, "file_id": file_id}
        row = self._db.q_one(sql, params)
        if row is None:
            sql = (
                "insert into files (message_id, file_id) values (:message_id, :file_id)"
            )
            self._db.u(sql, params)

    def add_image(self, url: str) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = "select 1 from images where message_id = :message_id and url = :url"
        params = {"message_id": self.id, "url": url}
        row = self._db.q_one(sql, params)
        if row is None:
            sql = "insert into images (message_id, url) values (:message_id, :url)"
            self._db.u(sql, params)

    def add_location(
        self, lat: decimal.Decimal, lng: decimal.Decimal, name: str
    ) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = """
            select 1 from locations
            where message_id = :message_id
              and lat = :lat and lng = :lng and name = :name
        """
        params = {"message_id": self.id, "lat": lat, "lng": lng, "name": name}
        row = self._db.q_one(sql, params)
        if row is None:
            sql = """
                insert into locations (message_id, lat, lng, name)
                values (:message_id, :lat, :lng, :name)
            """
            self._db.u(sql, params)

    def add_mention(self, user_id: int, location: int, length: int) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = """
            select 1 from mentions
            where message_id = :message_id
            and user_id = :user_id and location = :location and length = :length
        """
        params = {
            "message_id": self.id,
            "user_id": user_id,
            "location": location,
            "length": length,
        }
        row = self._db.q_one(sql, params)
        if row is None:
            sql = """
                insert into mentions (message_id, user_id, location, length)
                values (:message_id, :user_id, :location, :length)
            """
            self._db.u(sql, params)

    def add_video(self, preview_url: str, url: str) -> None:
        if self.id is None or self.find_by_id(self.id) is None:
            return
        sql = """
            select 1 from videos
            where message_id = :message_id and preview_url = :preview_url and url = :url
        """
        params = {"message_id": self.id, "preview_url": preview_url, "url": url}
        row = self._db.q_one(sql, params)
        if row is None:
            sql = """
                insert into videos (message_id, preview_url, url)
                values (:message_id, :preview_url, :url)
            """
            self._db.u(sql, params)

    def find_by_id(self, id_: int | None) -> Optional["Message"]:
        sql = """
            select
                avatar_url, created_at, id, name, sender_id, sender_type, source_guid,
                system, message_text, user_id
            from messages
            where id = :id
        """
        row = self._db.q_one(sql, {"id": id_})
        if row is None:
            return None
        return self

    def find_first_id(self) -> int:
        return self._db.q_val("select min(id) from messages")

    def find_last_id(self) -> int:
        return self._db.q_val("select max(id) from messages")

    def from_api(self, data: dict) -> None:
        if self.find_by_id(int(data["id"])) is None:
            self.avatar_url = data["avatar_url"]
            self.created_at = datetime.datetime.fromtimestamp(
                data["created_at"], tz=datetime.UTC
            )
            self.id = int(data["id"])
            self.name = data["name"]
            self.sender_id = data["sender_id"]
            self.sender_type = data["sender_type"]
            self.source_guid = data["source_guid"]
            self.system = data["system"]
            self.message_text = data["text"]
            self.user_id = data["user_id"]
            self.save()
            for attachment in data["attachments"]:
                type_ = attachment["type"]
                if type_ in ("image", "linked_image"):
                    self.add_image(attachment["url"])
                elif type_ == "file":
                    self.add_file(attachment["file_id"])
                elif type_ == "mentions":
                    for i, user_id in enumerate(attachment["user_ids"]):
                        self.add_mention(
                            int(user_id),
                            attachment["loci"][i][0],
                            attachment["loci"][i][1],
                        )
                elif type_ == "video":
                    self.add_video(attachment["preview_url"], attachment["url"])
                elif type_ == "emoji":
                    for charmap in attachment["charmap"]:
                        self.add_emoji(
                            attachment["placeholder"], charmap[0], charmap[1]
                        )
                elif type_ == "event":
                    self.add_event(attachment["event_id"], attachment["view"])
                elif type_ == "location":
                    lat = decimal.Decimal(attachment["lat"])
                    lng = decimal.Decimal(attachment["lng"])
                    self.add_location(lat, lng, attachment["name"])
                elif type_ == "autokicked_member":
                    self.add_autokicked_member(attachment["user_id"])
                else:
                    self._db.log.warning(f"Unsupported attachment type: {type_!r}")
                    self._db.log.warning(json.dumps(data, indent=1, sort_keys=True))

    def save(self) -> "Message":
        if self.find_by_id(self.id) is None:
            sql = """
                insert into messages (
                    avatar_url, created_at, id, name, sender_id,
                    sender_type, source_guid, system, message_text, user_id
                ) values (
                    :avatar_url, :created_at, :id, :name, :sender_id,
                    :sender_type, :source_guid, :system, :message_text, :user_id
                )
            """
        else:
            sql = """
                update messages
                set avatar_url = :avatar_url,
                    created_at = :created_at,
                    name = :name,
                    sender_id = :sender_id,
                    sender_type = :sender_type,
                    source_guid = :source_guid,
                    system = :system,
                    message_text = :message_text,
                    user_id = :user_id
                where id = :id
            """
        params = {
            "avatar_url": self.avatar_url,
            "created_at": self.created_at,
            "id": self.id,
            "name": self.name,
            "sender_id": self.sender_id,
            "sender_type": self.sender_type,
            "source_guid": self.source_guid,
            "system": self.system,
            "message_text": self.message_text,
            "user_id": self.user_id,
        }
        self._db.u(sql, params)
        self._db.log.info(f"Saved message {self.id}")
        return self


class Config:
    database: pathlib.Path
    group_id: int
    log_format: str
    log_level: str
    token: str | None

    def __init__(self) -> None:
        self.database = pathlib.Path(os.getenv("DATABASE", "")).resolve()
        self.group_id = int(os.getenv("GROUP_ID", 0))
        self.log_format = os.getenv(
            "LOG_FORMAT", "%(levelname)s [%(name)s] %(message)s"
        )
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.token = os.getenv("TOKEN")


def main() -> None:
    config = Config()
    logging.basicConfig(format=config.log_format, level="DEBUG", stream=sys.stdout)
    logging.debug(f"groupme-backup {__version__}")
    if config.log_level != "DEBUG":
        logging.debug(f"Changing log level to {config.log_level}")
    logging.getLogger().setLevel(config.log_level)

    db = Database(str(config.database))
    db.migrate()
    forward = True
    last_id = Message(db).find_last_id()
    if last_id is None:
        logging.info("Starting at the last message and saving all previous messages")
        forward = False
    else:
        logging.info(f"Looking for messages after {last_id}")
    params = {"token": config.token, "limit": 100}
    while True:
        data = httpx.get(
            f"https://api.groupme.com/v3/groups/{config.group_id}/messages",
            params=params,
        )
        if data.status_code != 200:
            logging.error(data.text)
            break
        messages = data.json()["response"]["messages"]
        if len(messages) < 1:
            break
        for message in data.json()["response"]["messages"]:
            Message(db).from_api(message)
        if forward:
            params["after_id"] = Message(db).find_last_id()
        else:
            params["before_id"] = Message(db).find_first_id()


if __name__ == "__main__":
    main()
