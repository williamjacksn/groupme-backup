create table sqlite_master (
  type,
  name
);

create table emoji (
    message_id integer,
    placeholder text,
    pack_id integer,
    offset integer
);

create table files (
    message_id integer,
    file_id text
);

create table images (
    message_id integer,
    url text
);

create table mentions (
    message_id integer,
    user_id integer,
    location integer,
    length integer
);

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
);

create table videos (
    message_id integer,
    preview_url text,
    url text
);

create table schema_versions (
    schema_version integer,
    migration_date timestamp
);

create table autokicked_members (
    message_id integer,
    user_id text
);

create table events (
    message_id integer,
    event_id text,
    view text
);

create table locations (
    message_id integer,
    lat decimal,
    lng decimal,
    name text
);
