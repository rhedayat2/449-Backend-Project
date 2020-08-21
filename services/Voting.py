
from MicroserviceBase import MicroserviceBase

from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

import sqlite3


class Voting(MicroserviceBase):

	def __init__(self, logName, app: FlaskAPI):

		self.__app = app

		super().__init__(logName, app)


    	#upvote
	def up_vote_post(self, post_id):

		parameters = {
			"post_id": post_id
		}

		upvote = self.query("upvote_post.sql", parameters)

		return upvote

	#downvote
	def down_vote_post(self, post_id):
		parameters = {
			"post_id": post_id
		}

		downvote = self.query("downvote_post.sql", parameters)

		return downvote


	#sort posts by score
	def post_by_score(self, count):
		parameters = {
			"count": count
		}

		top_posts = self.query("post_by_votes.sql", parameters)
		myList = list(top_posts)

		return myList


	#Report number of upvotes and downvotes for a post
	def get_post_with_id(self, post_id):
		parameters = {
			"post_id": post_id
		}

		post = self.query("post_by_id.sql", parameters)

		return post

	def vote_exists(self, post_id):
		parameters = {
			"post_id": post_id
		}
		post = self.query("VoteExists.sql", parameters)
		return post

	#given a list of post identifiers, return the list sorted by score
	def list_sorted(self, post_ids: list):
		parameters = {}

		sql = "SELECT post_id FROM vote WHERE post_id IN (Post_ids) GROUP BY post_id ORDER BY upvotes - downvotes DESC;"

		the_ids = self.create_query_list_bindings(post_ids, parameters)
		sql = sql.replace("Post_ids", the_ids)

		rows = self.query_raw(sql, parameters)
		if rows is None:
			return None

		id_sorted = list()
		for x in rows:
			id_sorted.append(x["post_id"])

		for post_id in post_ids:
			if post_id not in id_sorted:
				id_sorted.append(post_id)

		return id_sorted
