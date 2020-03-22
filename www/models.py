#!/usr/bin/env python
# _*_ coding: utf-8 _*_


import time
import uuid

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class Album(Model):
    __table__ = 'album'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    album_name = StringField(ddl='varchar(500)')
    origin_name = StringField(ddl='varchar(500)')
    name_keys = StringField(ddl='varchar(500)')
    story_count = IntegerField()
    cover = StringField(ddl='varchar(500)')
    description = TextField()
    is_publish = BooleanField()
    created_at = FloatField(default=time.time)
    updated_at = FloatField(default=time.time)


class Story(Model):
    __table__ = 'story'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    album_id = StringField(ddl='varchar(50)')
    story_name = StringField(ddl='varchar(500)')
    token = StringField(ddl='varchar(50)')
    order_in_album = IntegerField()
    play_url = StringField(ddl='varchar(500)')
    backup_url = StringField(ddl='varchar(500)')
    audio_type = StringField(ddl='varchar(50)')
    enable = BooleanField()
    created_at = FloatField(default=time.time)
    updated_at = FloatField(default=time.time)


class PlayStatus(Model):
    __table__ = 'play_status'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    device_id = StringField(ddl='varchar(50)')
    token = StringField(ddl='varchar(50)')
    offset = StringField(ddl='varchar(50)')
    finished = BooleanField()
    finished_times = IntegerField()
    updated_at = FloatField(default=time.time)


class PlayIndex(Model):
    __table__ = 'play_index'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    device_id = StringField(ddl='varchar(50)')
    album_id = StringField(ddl='varchar(50)')
    token = StringField(ddl='varchar(50)')
    updated_at = FloatField(default=time.time)

class StatisticView(Model):
    __table__ = 'statistic_view'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    device_id = StringField(ddl='varchar(50)')
    album_id = StringField(ddl='varchar(50)')
    album_name = StringField(ddl='varchar(500)')
    token = StringField(ddl='varchar(50)')
    story_id = StringField(ddl='varchar(50)')
    story_name = StringField(ddl='varchar(500)')
    offset = StringField(ddl='varchar(50)')
    finished = BooleanField()
    finished_times = IntegerField()
    updated_at = FloatField(default=time.time)
    current_token = BooleanField()
