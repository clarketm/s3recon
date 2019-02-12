import re
from enum import Enum
from functools import wraps
from logging import getLogger, basicConfig, INFO

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError

logger = getLogger(__name__)

basicConfig(format="%(message)s", level=INFO)


def with_retry(tries):
    def outer_wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            def _retry(t=tries):
                if t <= 0:
                    logger.error("unable to write hit to database")
                    # raise WriteError(f"unable to write to database")
                    return
                try:
                    f(*args, **kwargs)
                except PyMongoError:
                    t -= 1
                    _retry(t)

            return _retry()

        return inner_wrapper

    return outer_wrapper


class StringEnum(Enum):
    def __str__(self):
        return str(self.value["text"])

    def __repr__(self):
        return str(self.value["key"])


class Access(StringEnum):
    PUBLIC = {"key": "+", "text": "public"}
    PRIVATE = {"key": "-", "text": "private"}


class Hit:
    def __init__(self, url: str, access: Access):
        self.url = url
        self.access = access

    def __iter__(self):
        yield from {"url": self.url, "access": str(self.access)}.items()

    def is_valid(self):
        return (
            re.match(r"^https?://.*\.amazonaws.com/.*$", self.url)
            and self.access in Access
        )


class MongoDB:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 27017,
        db_name: str = "s3recon",
        col_name: str = "hits",
        unique_indicies: tuple = ("url",),
        indicies: tuple = ("access",),
        timeout: int = 10,
    ):
        self.client = MongoClient(host, port, serverSelectionTimeoutMS=timeout)
        self.db_name = db_name
        self.col_name = col_name
        self.index(unique_indicies, unique=True)
        self.index(indicies)

    def __del__(self):
        self.client.close()

    def index(self, indicies=(), **kwargs):
        for i in indicies:
            self.client[self.db_name][self.col_name].ensure_index(i, **kwargs)

    @staticmethod
    def normalize(item):
        if isinstance(item, (list, set)):
            return list(map(dict, item))
        else:
            return dict(item)

    @with_retry(3)
    def insert_many(self, items):
        self.client[self.db_name][self.col_name].insert_many(self.normalize(items))

    @with_retry(3)
    def insert(self, item):
        self.client[self.db_name][self.col_name].insert(self.normalize(item))

    @with_retry(3)
    def update_many(self, filter, items):
        self.client[self.db_name][self.col_name].update_many(
            filter, self.normalize(items), upsert=True
        )

    @with_retry(3)
    def update(self, filter, item):
        self.client[self.db_name][self.col_name].update(
            filter, self.normalize(item), upsert=True
        )

    def is_connected(self):
        try:
            self.client.server_info()
        except ServerSelectionTimeoutError:
            return False
        return True
