from flask import request
from flask_api import FlaskAPI, status


import calendar
import os
import random
import sqlite3
import threading
import time

DATABASE = '../database/project1.db'

class MicroserviceBase:

	__sqls_dirname = "sqls"

	def __init__(self, log_name, app: FlaskAPI):

		self.__log_name = log_name
		self.__app = app

		self.__db_path = self.get_db_path()
		self.__db_connections = dict()

		self.ensure_database_connected()

	def log(self, s, o=None):

		to_print = "[" + self.__log_name + "] " + str(s)

		if o is not None:
			to_print += "\n" + str(o)

		print(to_print)

	@staticmethod
	def timestamp():

		"""
		Snippet from:
		https://stackoverflow.com/questions/4548684/how-to-get-the-seconds-since-epoch-from-the-time-date-output-of-gmtime
		"""
		return calendar.timegm(time.gmtime())

	def get_db_path(self):

		return self.__app.config["DB_PATH"]

	def ensure_database_connected(self):

		my_thread_id = threading.get_ident()
		if my_thread_id in self.__db_connections.keys():
			return self.__db_connections[my_thread_id]

		conn = self.connect_to_database()
		self.remember_database_connection(conn)

		self.query("../../operations/sqls/initialize.sql")

		return conn

	def connect_to_database(self):

		return sqlite3.connect(DATABASE)

	def remember_database_connection(self, conn):

		my_thread_id = threading.get_ident()

		self.__db_connections[my_thread_id] = conn

	def get_db(self):

		return self.ensure_database_connected()

	def make_sql_path(self, name):

		return os.path.join(
			self.__sqls_dirname,
			name
		)

	def load_sql(self, name):

		f = open(self.make_sql_path(name))
		sql = f.read()

		return sql

	def query(self, sql_name, params=None):

		sql = self.load_sql(sql_name)

		return self.query_raw(sql, params)

	def query_raw(self, sql, params=None):

		db: sqlite3.connect = self.get_db()

		crsr = db.cursor()

		try:
			print("PARAMS:::::", params)
			if params is None:
				crsr = db.executescript(sql)
			else:
				crsr = db.execute(sql, params)

		except sqlite3.OperationalError as e:
			self.log("Exception while executing sql: " + sql)
			raise e

		rows = self.fetch_cursor_rows(crsr)
		if len(rows) == 0:
			rows = None

		#rows = cursor.fetchall()

		#cursor.close()
		crsr.close()

		db.commit()

		return rows

	# Modified from: https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
	@staticmethod
	def fetch_cursor_rows(cursor):

		rows = list()

		for row in cursor.fetchall():

			d = {}

			for idx, col in enumerate(cursor.description):
				d[col[0]] = row[idx]

			rows.append(d)

		return rows

	# Dynamically generate SQL and modify a parameter list to support "IN(some list)"
	@staticmethod
	def create_query_list_bindings(the_list: list, parameters):

		if isinstance(parameters, list):
			pass
		elif isinstance(parameters, dict):
			pass
		else:
			raise ValueError("Argument 'parameters' should be a list or dict")

		main_key = random.randint(1000000000, 3000000000)

		binding_names = list()
		for i in range(len(the_list)):

			item = the_list[i]

			if isinstance(parameters, list):
				parameters.append(item)
				binding_names.append("?")
			else:
				key = "list_binding_" + str(main_key) + "_" + str(i)
				parameters[key] = item
				binding_names.append(":" + key)

		binding_names_formatted = ", ".join(binding_names)

		return binding_names_formatted

	@staticmethod
	def error(message, status_code=None):

		if status_code is None:
			status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

		data = {
			"error": message
		}

		return data, status_code

	def error404(self, message=None):

		if message is None:
			message = "Not found"

		return self.error(message, status.HTTP_404_NOT_FOUND)

	@staticmethod
	def ok(message=None, extra_data: dict = None):

		response = {
			"result": "OK",
			"message": message
		}

		if extra_data is not None:
			response.update(extra_data)

		return response

	@staticmethod
	def demand_post_values(keys):

		for k in keys:
			val = request.data.get(k, "")
			if val == "":
				return "Missing key: " + k

		return None
