# -*- coding: utf-8 -*-
import mysql.connector
import newsspider.settings
class DBService(object):
    def _start_context(self):
        context = mysql.connector.connect(
            host = newsspider.settings.DB_HOST,
            port = newsspider.settings.DB_PORT,
            user = newsspider.settings.DB_USERNAME,
            password = newsspider.settings.DB_PASSWORD,
            database = newsspider.settings.DB_NAME,
            charset = 'utf8'
        )
        return context
    def executeQuery(self,sql,data=None):
        context = self._start_context()
        cursor = context.cursor()
        cursor.execute(sql,data)
        l = []
        for tmp in cursor:
            l.append(tmp)
        cursor.close()
        context.close()
        return l

