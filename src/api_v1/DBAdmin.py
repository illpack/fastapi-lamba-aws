#!/usr/bin/python
import logging
import sys
import time
import os

import psycopg2

dbconfig = {
    "host": os.environ.get("HOST"),
    "user": os.environ.get("USER"),
    "password": os.environ.get("PASSWORD"),
    "port": os.environ.get("PORT"),
    "database": os.environ.get("DATABASE"),
}

class DBAdmin:
    def __init__(self, logger=None, verbose=True):
        self.db_params = dbconfig
        self._verbose = verbose
        self.log = logger or logging.getLogger('default')
        self.log_msg = 'Executing:\n----------\n{}\n'

    def query_returns(self, sql):
        args = [a.upper() for a in sql.split(' ')]
        if 'RETURNING' in args or 'SELECT' in args:
            return True
        else:
            return False

    def sanitize_args(self, sql: str) -> None:
        # Sanitize input params
        args = [a.upper() for a in sql.split(' ')]
        words = [';', 'DROP', 'DELETE', 'DATABASE', 'DBCC', 'WRITEPAGE']
        if any(x in item for x in words for item in args):
            raise AssertionError

    def connect(self):
        """Connect to the PostgreSQL database server"""
        conn = None
        try:
            # read connection parameters
            conn = psycopg2.connect(**self.db_params)
            # create a cursor
            return conn
        except Exception as error:
            self.log.error(error)
            raise

    def query(self, sql, commit=False, sanitize=True):
        conn = None
        try:
            start = time.time()
            if sanitize is True:
                self.sanitize_args(sql)
            conn = self.connect()
            cur = conn.cursor()
            if self._verbose:
                self.log.debug(self.log_msg.format(sql))
            cur.execute(sql)
            if commit:
                conn.commit()
            if self.query_returns(sql):
                sql = cur.fetchall()
            cur.close()
            if self._verbose:
                self.log.debug(f'Completed in {round(time.time()-start, 3)}s.')
            return sql
        except AssertionError:
            msg = f'Injected arguments are potentially dangerous:\n\n{sql}'
            self.log.error(msg)
            if conn is not None:
                conn.rollback()
            raise ValueError(msg)
        except Exception as error:
            self.print_psycopg2_exception(error)
        finally:
            if conn is not None:
                conn.close()

    class DBError(Exception):
        pass

    # define a function that handles and parses psycopg2 exceptions
    def print_psycopg2_exception(self, err):
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno

        # print the connect() error
        msg = f"SQL ERROR:\n{str(err)}on line number: {line_num} | type: {err_type}"
        self.log.error(msg)
        raise self.DBError(err)


if __name__ == '__main__':
    db = DBAdmin(logger=logging.getLogger('default'))
    try:
        data = db.read("SELECT * from variants WHERE image_file_name = 'jjjjj'")
        print(data)
    except NameError as e:
        print(e)
    except db.DBError as e:
        print(e)
