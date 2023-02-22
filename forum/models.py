import datetime
import uuid

from cassandra.cqlengine import columns
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django_cassandra_engine.models import DjangoCassandraModel


class Users(DjangoCassandraModel, AbstractUser):
    __table_name__ = "users"
    __keyspace__ = "forumKeySpace"

    name = columns.Text(required=True)

    username = columns.UUID(primary_key=True, default=uuid.uuid4)

    email = columns.Text(index=True, required=True)
    password = columns.Text(required=True, min_length=6)

    authenticated = columns.Boolean(required=True, default=False)

    date_joined = columns.DateTime(required=True, default=datetime.datetime.now)

    is_staff = columns.Boolean(required=True, default=False)
    is_superuser = columns.Boolean(required=True, default=False)
    is_active = columns.Boolean(required=True, default=False)

    last_login = columns.DateTime(required=False)

    profile_url = columns.Text(required=False, default="/static/img/default-user.png")


class Thread(DjangoCassandraModel):
    __table_name__ = "thread"
    __keyspace__ = "forumKeySpace"

    thread_id = columns.UUID(primary_key=True, default=uuid.uuid4)

    topic = columns.Text(min_length=0, required=True)
    author = columns.UUID(required=True)

    date_posted = columns.DateTime(required=True, default=datetime.datetime.now)

    views = columns.Integer(required=True, default=0)
    replies = columns.Integer(required=True, default=0)

    tags = columns.Set(columns.Text, strict=True)

    is_active = columns.Boolean(required=True, default=True)


class ThreadContent(DjangoCassandraModel):
    __table_name__ = "thread_content"
    __keyspace__ = "forumKeySpace"

    thread_id = columns.UUID(primary_key=True)
    content = columns.Text(required=True)

    last_modified = columns.DateTime()



