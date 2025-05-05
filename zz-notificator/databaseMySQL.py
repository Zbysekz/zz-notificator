#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import time
import sys
import os
from datetime import datetime,timezone
import threading
import pathlib
from parameters import Parameters
from logger import Logger
thisScriptPath = str(pathlib.Path(__file__).parent.absolute())


def ThreadingLockDecorator(func):
    def wrapper(*args, **kwargs):
        #cMySQL.mySQLLock.acquire()
        ret = func(*args, **kwargs)
        #cMySQL.mySQLLock.release()
        return ret

    return wrapper

class cMySQL:
    mySQLLock = threading.Lock()

    def __init__(self):
        self._persistentConnection = False
        self.databaseCon = None
        self.logger = Logger("databaseMySQL", verbosity=Parameters.VERBOSITY)

    def getConnection(self):
        if self._persistentConnection:
            return self.databaseCon, self.databaseCon.cursor()
        else:
            db = self.init_db()
            return db, db.cursor()

    def PersistentConnect(self):

        self._persistentConnection = True
        self.databaseCon = self.init_db()

    def PersistentDisconnect(self):
        self._persistentConnection = False
        self.databaseCon.close()

    def init_db(self):
        #for line in traceback.format_stack():
        #    print(line.strip())
        return mysql.connector.connect(
            host="localhost",
            user="mainScript",
            password=Parameters.DB_PWD,
            database="db1",
            connection_timeout=10
        )

    def closeDBIfNeeded(self, conn):
        if not self._persistentConnection:
            conn.close()

    @ThreadingLockDecorator
    def getQueue(self):
        try:
            db, cursor = self.getConnection()

            sql = "SELECT id, receiver, subject, message FROM notificator_queue WHERE state='CREATED'"
            cursor.execute(sql)

            result = cursor.fetchall()

            result = {}
            for x in result:
                result["id"] = x[0]
                result["receiver"] = x[1]
                result["subject"] = x[2]
                result["message"] = x[3]

            cursor.close()
            self.closeDBIfNeeded(db)

        except Exception as e:
            self.logger.log("Error while reading notificator queue, exception:")
            self.logger.log_exception(e)
            return None

        return result

    def reportSentResult(self, result):

        ok_ids = [x["id"] for x in result if x["result"] == "ok"]

        if len(ok_ids)>0:
            try:
                db, cursor = self.getConnection()

                sql = f"UPDATE notificator_queue SET state='SENT' WHERE id in ({','.join(ok_ids)})"
                cursor.execute(sql)

                cursor.close()
                self.closeDBIfNeeded(db)

            except Exception as e:
                self.logger.log("Error while writing notificator responses, exception:")
                self.logger.log_exception(e)

        for i in [x for x in result if x["result"] != "ok"]:
            try:
                db, cursor = self.getConnection()

                sql = f"UPDATE notificator_queue SET state='ERROR', error_type='{i['error_type']}', error_message='{i['error_message']}' WHERE id = {i['id']})"

                cursor.execute(sql)

                cursor.close()
                self.closeDBIfNeeded(db)

            except Exception as e:
                self.logger.log("Error while writing notificator responses, exception:")
                self.logger.log_exception(e)

