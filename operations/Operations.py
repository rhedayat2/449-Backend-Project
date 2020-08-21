

import json
import os
import random
import requests
import sqlite3


from flask_api import status as flask_api_status


class Operations:
	
	__log_name = "Operations"
	__sqls_dirname = "sqls"
	
	__microservice_posting_urlPrefix = "/posts"
	__microservice_voting_urlPrefix = "/votes"
	__api_urlPrefix = "/v1/"
	
	def __init__(self, db_path):
		
		if db_path == "":
			raise Exception("Whoops ... blank db path")
		
		self.__db_path = db_path
		self.__db = None
	
	def log(self, s, o=None):
	
		to_print = "[" + self.__log_name + "] " + str(s)
		
		if o is not None:
			to_print += "\n" + str(o)
		
		print(to_print)
	
	def ensure_database_connected(self):
		
		if self.__db is None:
			self.connect_to_database()
		
		return self.__db
	
	def clear_database(self):
		
		db_path = self.get_db_path()
		if os.path.isfile(db_path):
			os.remove(db_path)
		
		return self.get_db()
	
	def connect_to_database(self):
		
		self.__db = sqlite3.connect(self.__db_path)
	
	def get_db_path(self):
		
		return self.__db_path
	
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
	
	def query(self, sql_name):
		
		db: sqlite3.Connection = self.get_db()
		sql = self.load_sql(sql_name)
		
		try:
			db.execute(sql)
		except sqlite3.OperationalError as e:
			self.log("Exception while executing sql: " + sql_name)
			raise e
	
	def query_script(self, sql_name):
		
		db: sqlite3.Connection = self.get_db()
		sql = self.load_sql(sql_name)
		
		try:
			db.executescript(sql)
		except sqlite3.OperationalError as e:
			self.log("Exception while executing sql: " + sql_name)
			raise e
	
	def reinitialize_database(self):
		
		# Delete the entire file! OH DEAR!
		self.clear_database()
		
		#
		self.log("Initializing the database")
		self.query_script("initialize.sql")
	
	def populate_database(self, posting_port, voting_port):
		
		highest_post_id = self.populate_posts(posting_port)
		self.populate_votes(voting_port, highest_post_id)
	
	def populate_posts(self, port):
		
		self.log("Begin trying to populate posts")
		
		post_number = 1
		usernames = ["mike", "upal", "rahin"]
		communities = ["cats", "catstravaganza"]
		multiplier = 10
		for username in usernames:
			
			# Each user posts in each community
			for community in communities:
				
				# Each user will make multiplier posts in this community
				for i in range(multiplier):
					
					title = "My Test Post #" + str(post_number)
					text = "Hey just writing about whatever. La la la. \n\n Lar lar lar." \
						+ "\n\n\n(this was post #" + str(post_number)
					
					post = {
						"title": title,
						"text": text,
						"username": username,
						"community": community,
						"resource_url": self.grab_random_cat_image_url()
					}
					
					url = "http://localhost:" + str(port)
					url += self.__microservice_posting_urlPrefix + self.__api_urlPrefix + "resources/posts"
					
					self.log("Adding a new post ...")
					response = requests.post(url, json=post)
					if response.status_code != flask_api_status.HTTP_201_CREATED:
						self.log("Failed to post to API: " + url)
						raise Exception("Failed to post to API:" + str(response.content))
					
					post_number += 1
		
		self.log("Post population seems to have finished with no errors")
		
		return post_number - 1
		
	# https://docs.thecatapi.com/
	def grab_random_cat_image_url(self):
		
		response = requests.get("https://api.thecatapi.com/v1/images/search")
		if response.status_code != 200:
			self.log("Failed to pull a cat image from thecatapi.com")
			return None
		
		data = response.json()[0]
		return data["url"]
	
	def populate_votes(self, port, highest_post_id):
		
		self.log("Begin trying to populate votes")
		
		populator_id = random.randint(1000000000, 9999999999)
		
		vote_count = 250
		vote_number = 1
		for i in range(vote_count):
			
			r = random.randrange(0, 2)
			if r == 0:
				direction = "up"
			else:
				direction = "down"
			
			post_id = str(random.randrange(1, highest_post_id + 1))
			username = "populator_" + str(populator_id) + "_" + str(i)
			data = {
				"username": username,
				"direction": direction
			}
			url = "http://localhost:" + str(port)
			url += self.__microservice_voting_urlPrefix
			url += self.__api_urlPrefix + "resources/votes/post/" + str(post_id)
			
			self.log("Sending " + direction + "vote to post " + str(post_id) + "(" + username + ")")
			response = requests.post(url, json=data)
			if response.status_code != 200:
				self.log("Failed to post to API: " + url)
				raise Exception("Failed to post to API:" + str(response.content))
			
			vote_number += 1
		
		self.log("Vote population seems to have finished with no errors")
	
	def test_posting(self, port: int):
		
		# URLs
		url_prefix = "http://localhost:" + str(port) \
			+ self.__microservice_posting_urlPrefix \
			+ self.__api_urlPrefix
		url_add_post = url_prefix + "resources/posts"
		url_latest_global_posts = url_prefix + "resources/posts"
		url_latest_community_posts_base = url_prefix + "resources/community/%%%COMMUNITY%%%/posts"
		
		self.log("Testing the posting microservice")
		self.log("Using url prefix: " + url_prefix)
		self.log("Using add-post url: " + url_add_post)
		self.log("Using latest global posts url: " + url_latest_global_posts)
		self.log("Using latest community posts base url: " + url_latest_community_posts_base)
		
		my_errors = list()
		
		# Setup a base post to add
		base_post = {
			"title": "Hello from tester",
			"text": "This is just a test post from the automated tester",
			"community": "bots",
			"username": "mike"
		}
		
		# Try to add a bunch of bad posts
		# (each attempt is missing a different required key)
		try:
			missing_keys = ["title", "text", "community", "username"]
			for k in missing_keys:
				post = base_post.copy()
				post.pop(k, None)
				try:
					self.log("Submitting invalid post (missing key \"" + k + "\")")
					response = requests.post(url_add_post, json=post)
				except requests.exceptions.ConnectionError:
					raise AssertionError("Test FAILED: Unable to connect!")
				if response.status_code == 201:
					raise AssertionError("Somehow succeeded in submitting a BAD POST: " + str(post))
				elif response.status_code == 400:
					self.log("Test successfully submitted a bad request")
				else:
					raise AssertionError(
						"Unexpected status code from server: " + str(response.status_code)
					)
		except AssertionError as e:
			s = "Testing failed to test for bad submissions: " + str(e)
			self.log(s)
			my_errors.append(s)
		
		# Try to successfully add a post
		post = None
		new_post_location = None
		try:
			post = base_post.copy()
			self.log("Submitting valid post")
			
			response = requests.post(url_add_post, json=post)
			
			if response.status_code != flask_api_status.HTTP_201_CREATED:
				raise AssertionError("Didn't get HTTP_201_CREATED response code for new post submission")
			
			if "Location" not in response.headers.keys():
				raise AssertionError("No location header in response")
			new_post_location = response.headers["Location"]
			self.log("Successfully submitted new post: \n" + str(response.content.decode()))
			self.log("Location header was: " + new_post_location)
		except AssertionError as e:
			s = "Testing failed to submit valid submissions: " + str(e)
			self.log(s)
			my_errors.append(s)
		
		# Check that the post we added does indeed exist
		if post is None or new_post_location is None:
			s = "Cannot check that our newly added post exists, because we already failed to add it"
			self.log(s)
			my_errors.append(s)
		else:
			response = None
			try:
				
				self.log("Verifying we can fetch the new post at: " + new_post_location)
				
				response = requests.get(new_post_location)
				if response.status_code == 404:
					raise AssertionError("Unable to find the newly created post")
				elif response.status_code == 200:
					self.log("We seem to have successfully fetched the newly created post")
				else:
					raise AssertionError("Unknown error")
				
				# Validate the data
				self.log("Validating post data")
				new_post = json.loads(response.content.decode())
				for k in base_post.keys():
					if k not in post.keys():
						raise AssertionError("Post was missing key: " + k)
					elif new_post[k] == base_post[k]:
						self.log("Validated key \"" + k + "\": " + str(new_post[k]))
					else:
						raise AssertionError(
							"Data mismatch at key: " + k
							+ "\n Expected: " + base_post[k]
							+ "\n Actual: " + new_post[k]
						)
				self.log("Post data seems to be valid")
				
			except AssertionError as e:
				s = "Testing failed to fetch the newly created post:" \
					+ "\n Status: " + str(response.status_code) \
					+ "\n " + str(e)
				self.log(s)
				my_errors.append(s)
		
		# Delete the post we just created
		if post is None or new_post_location is None:
			s = "Cannot try to delete our newly added post exists, because we already failed to add it"
			self.log(s)
			my_errors.append(s)
		else:
			response = None
			try:
				response = requests.delete(new_post_location)
				if response.status_code == flask_api_status.HTTP_200_OK:
					self.log("We seem to have successfully deleted the newly created post")
				else:
					raise AssertionError("Unknown error")
				# Make sure the post was actually deleted
				response = requests.delete(new_post_location)
				if response.status_code == flask_api_status.HTTP_404_NOT_FOUND:
					self.log("Deletion of our created post seems to have succeeded")
				else:
					raise AssertionError("Deletion of our created post didn't seem to succeed")
			except AssertionError as e:
				s = "Testing failed to delete the newly created post:" \
					+ "\n Status: " + str(response.status_code) \
					+ "\n " + str(e)
				self.log(s)
				my_errors.append(s)
		
		# Grab N most recent posts to particular communities (or global)
		for community in list(["cats", None]):
			
			if community is None:
				label = "Global"
				url = url_latest_global_posts
			else:
				label = "Community::" + community
				url = url_latest_community_posts_base.replace("%%%COMMUNITY%%%", community)
			
			for posts_count in range(0, 10):
				response = None
				try:
					self.log("Trying to fetch latest " + str(posts_count) + " " + label + " posts: " + url)
					response = requests.get(url + "?count=" + str(posts_count))
					if response.status_code != flask_api_status.HTTP_200_OK:
						raise AssertionError("Failed to grab most recent " + label + " posts: " + url)
					the_json = response.content.decode()
					posts = json.loads(the_json)
					if len(posts) != posts_count:
						raise AssertionError(
							"Didn't get back correct number of posts"
							+ "; Wanted " + str(posts_count) + " but got " + str(len(posts))
						)
					self.log("Got back correct count of recent community posts: " + str(posts_count))
				except AssertionError as e:
					s = "Testing failed to get latest community posts:" \
						+ "\n Status: " + str(response.status_code) \
						+ "\n " + str(e)
					self.log(s)
					my_errors.append(s)
		
		if len(my_errors) == 0:
			self.log("Seems like the posting microservice passed all tests")
		else:
			self.log("Failed to test posting with one or more error messages:")
			for s in my_errors:
				self.log("Error: " + str(s))
	
	def test_voting(self, port: int):
		
		# URLs
		url_prefix = "http://localhost:" + str(port) + self.__microservice_voting_urlPrefix + self.__api_urlPrefix
		url_post_votes_base = url_prefix + "resources/votes/post"
		url_top_community_posts = url_prefix + "resources/votes/community/%%%COMMUNITY%%%/top/%%%COUNT%%%"
		url_top_global_posts = url_prefix + "resources/votes/top/%%%COUNT%%%"
		url_sorted_posts = url_prefix + "resources/votes/posts/sort"
		
		self.log("Testing the voting microservice")
		self.log("Using url prefix: " + url_prefix)
		self.log("Using vote-on-post url base: " + url_post_votes_base)
		self.log("Using top community posts template: " + url_top_community_posts)
		self.log("Using top global posts template: " + url_top_global_posts)
		self.log("Using sorted posts template: " + url_sorted_posts)
		
		my_errors = list()
		
		self.log("Try to vote on a post that doesn't exist (super high number)")
		impossible_post_id = 1000000000
		url_404_votes = url_post_votes_base + "/" + str(impossible_post_id)
		try:
			
			data = {
				"post_id": impossible_post_id,
				"direction": "up",
				"username": "mike"
			}
			
			response = requests.post(url_404_votes, json=data)
			if response.status_code != flask_api_status.HTTP_409_CONFLICT:
				raise AssertionError(
					"Bad response code: " + str(response.status_code)
				)
		except AssertionError as e:
			s = "Failed to receive an error for voting on non-existant post: " + str(e)
			self.log(s)
			my_errors.append(s)
		
		url_post1_votes = url_post_votes_base + "/1"
		self.log("Retrieving votes for the first post: " + url_post1_votes)
		post_score = None
		try:
			response = requests.get(url_post1_votes)
			if response.status_code != flask_api_status.HTTP_200_OK:
				raise AssertionError("Bad response code: " + str(response.status_code))
			the_json = response.content.decode()
			post = json.loads(the_json)
			post_score = post["score"]
			self.log("Post has current score: " + str(post_score))
		except AssertionError as e:
			s = "Failed to retrieve current votes on post 1: " + str(e)
			self.log(s)
			my_errors.append(s)
		
		# Cast some upvotes and downvotes in an attempt to manipulate score
		if post_score is None:
			target_score = None
			s = "Cannot cast upvotes and downvotes because we failed to retrieve post 1's score"
			self.log(s)
			my_errors.append(s)
		else:
			self.log("Going to try and manipulate the score for post #1")
			upvote_adjustment = random.randint(10, 20)
			downvote_adjustment = random.randint(10, 20)
			if upvote_adjustment == downvote_adjustment:
				upvote_adjustment += 1
			target_score = post_score + upvote_adjustment - downvote_adjustment
			self.log("Going to try and upvote " + str(upvote_adjustment) + " times")
			self.log("Going to try and downvote " + str(downvote_adjustment) + " times")
			self.log("Target score: " + str(target_score))
			votes = list()
			votes.extend(["up"] * upvote_adjustment)
			votes.extend(["down"] * downvote_adjustment)
			manipulation_id = random.randint(1000000000, 9999999999)
			try:
				for vote_index in range(len(votes)):
					
					vote = votes[vote_index]
					
					url_post_votes = url_post_votes_base + "/1"
					
					# Use a special username to thwart system limiting each
					# user to only 1 vote per post
					voter_username = "manipulator_" + str(manipulation_id) + "_" + str(vote_index)
					
					data = {
						"post_id": 1,
						"direction": vote,
						"username": voter_username
					}
					
					response = requests.post(url_post_votes, json=data)
					if response.status_code != flask_api_status.HTTP_200_OK:
						raise AssertionError(
							"Bad response code: " + str(response.status_code)
							+ "\n" + str(response.content)
						)
					self.log("Vote successfully casted: " + voter_username + " ==> " + vote)
			except AssertionError as e:
				s = "Failed to cast votes on post #1: " + str(e)
				self.log(s)
				my_errors.append(s)
		
		if post_score is None or target_score is None:
			s = "Cannot check post score adjustments because we weren't able to check the post score in the first place"
			self.log(s)
			my_errors.append(s)
		else:
			self.log("Verifying we were able to adjust score for the first post (id=1)")
			try:
				response = requests.get(url_post_votes_base + "/1")
				if response.status_code != flask_api_status.HTTP_200_OK:
					raise AssertionError("Bad response code: " + str(response.status_code))
				the_json = response.content.decode()
				post = json.loads(the_json)
				new_post_score = post["score"]
				if new_post_score != target_score:
					raise AssertionError(
						"Failed to adjust post score"
						+ "; Wanted " + str(target_score) + " but got " + str(new_post_score)
					)
				self.log("Successfully adjusted post score to: " + str(new_post_score))
			except AssertionError as e:
				s = "Verification of adjusted post score failed: " + str(e)
				self.log(s)
				my_errors.append(s)
		
		# Load top N posts for communities (and global)
		# Make sure they're in order too
		for community in ["cats", None]:
			
			for count in list([1, 3, 9]):
				
				if community is None:
					label = "Global"
					url = url_top_global_posts
				else:
					label = "Community:" + community
					url = url_top_community_posts
					url = url.replace("%%%COMMUNITY%%%", community)
				
				url = url.replace("%%%COUNT%%%", str(count))
				
				self.log("Fetching the top " + str(count) + " posts from " + label + ": " + url)
				try:
					response = requests.get(url)
					if response.status_code != flask_api_status.HTTP_200_OK:
						raise AssertionError("Bad response code: " + str(response.status_code))
					the_json = response.content.decode()
					posts = json.loads(the_json)
					if len(posts) != count:
						raise AssertionError("Bad post count; Wanted " + str(count) + " but got " + str(len(posts)))
					
					# Check order
					if not self.are_posts_in_order(posts):
						raise AssertionError("Found an out of order post")
					self.log("Posts seem to be in order")
					
					self.log("Successfully grabbed top " + label + " posts")
					
				except AssertionError as e:
					s = "Failed to grab the top " + label + " posts: " + str(e)
					self.log(s)
					my_errors.append(s)
		
		# Give the API a list of posts, and expect they come back ordered
		self.log("Asking API to sort list of posts by score")
		posts_ids = "1,2,3,4,5,6,7,8,9,10"
		url = url_sorted_posts + "?ids=" + posts_ids
		try:
		
			response = requests.get(url)
			if response.status_code != flask_api_status.HTTP_200_OK:
				raise AssertionError("Bad response code: " + str(response.status_code))
			the_json = response.content.decode()
			response_data = json.loads(the_json)
			# print(response_data)
			
			last_score = None
			for post_id in response_data["ids_sorted"]:
				url_post_votes = url_post_votes_base + "/" + str(post_id)
				response = requests.get(url_post_votes)
				if response.status_code != flask_api_status.HTTP_200_OK:
					raise AssertionError("Failed to grab votes for post: " + url_post_votes)
				the_json = response.content.decode()
				post_info = json.loads(the_json)
				if last_score is not None and post_info["score"] > last_score:
					raise AssertionError("Found an out of order post: " + url_post_votes)
				last_score = post_info["score"]
			
			self.log("Successfully grabbed sorted list of posts")
		
		except AssertionError as e:
			s = "Failed to grab score-sorted list of posts from API: " + str(e)
			self.log(s)
			my_errors.append(s)
		
		if len(my_errors) == 0:
			self.log("Seems like the voting microservice passed all tests")
		else:
			self.log("Microservice failed tests with one or more errors:")
			for s in my_errors:
				self.log(s)
	
	@staticmethod
	def are_posts_in_order(posts):
		
		# Check order
		last_score = None
		for post in posts:
			score = post["score"]
			if last_score is not None and score > last_score:
				return False
			last_score = score
		
		return True
