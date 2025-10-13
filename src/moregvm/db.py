from contextlib import contextmanager

import psycopg2

import moregvm.config


@contextmanager
def db_connect():
    db_config = moregvm.config.database()
    with psycopg2.connect(db_config["dsn"]) as conn:
        yield conn


@contextmanager
def db_cursor():
    with db_connect() as conn:
        with conn.cursor() as curs:
            yield curs
