

from MicroserviceBase import MicroserviceBase
import Reddit


from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions


import rfeed


import datetime
import json
import pprint
import requests


"""
Snippets taken liberally from https://github.com/svpino/rfeed
"""


class BFF(MicroserviceBase):
	
	__api_prefix = None
	
	__posting_api_port_development = 8000
	__posting_api_port_production = 2015
	__posting_api_prefix = "/posts/v1/"
	
	__voting_api_port_development = 8001
	__voting_api_port_production = 2015
	__voting_api_prefix = "/votes/v1/"
	
	__api_timeout = 10
	
	__reasonable_hot_examination_limit = 500
	
	__development_mode = False
	
	def __init__(self, log_name, app: FlaskAPI, api_prefix):
		
		self.__app = app
		
		self.__api_prefix = api_prefix
		
		super().__init__(log_name, app)
	
	def set_development_mode(self, b: bool = True):
		
		print("BFF entering development mode")
		
		self.__development_mode = b
	
	@staticmethod
	def get_hostname_from_request(request):
		
		hostname, port = str(request.host).split(":")
		
		return hostname
	
	def make_posting_url(self, request_original, path):
		
		hostname = self.get_hostname_from_request(request_original)
		
		url = request_original.scheme + "://"
		url += hostname
		
		if self.__development_mode:
			
			url += ":" + str(self.__posting_api_port_development)
			
		else:
			
			url += ":" + str(self.__posting_api_port_production)
		
		url += self.__posting_api_prefix
		
		url += path
		
		return url
	
	def make_posting_post_url(self, request_original, post_id):
	
		return self.make_posting_url(request_original, "resources/post/" + str(post_id))
	
	def make_voting_url(self, request_original, path):
		
		hostname = self.get_hostname_from_request(request_original)
		
		url = request_original.scheme + "://"
		url += hostname
		
		if self.__development_mode:
			
			url += ":" + str(self.__voting_api_port_development)
		
		else:
			
			url += ":" + str(self.__voting_api_port_production)
		
		url += self.__voting_api_prefix
		
		url += path
		
		return url
	
	def make_voting_post_score_url(self, request_original, post_id):
		
		return self.make_voting_url(
			request_original,
			"resources/votes/post/" + str(post_id)
		)
	
	# TODO: What's going on with the "count" here?
	def get_recent_community_posts(self, request, community=None, count=None):
		
		if count is None:
			count = 25
		
		if community is None:
			path = "resources/posts"
		else:
			path = "resources/community/" + community + "/posts"
		
		url = self.make_posting_url(request, path)
		# print(url)
		
		api_posts = self.query_api(url)
		# print(data)
		
		return api_posts
	
	def get_recent_community_posts_feed(self, request, community=None, count=None):
		
		if count is None:
			count = 25
		
		if community is None:
			community_label = "any community"
		else:
			community_label = community
		
		api_posts = self.get_recent_community_posts(request, community, count)
		# print(data)
		
		feed = self.posts_to_feed(
			api_posts,
			title="Latest " + str(count) + " posts to " + community_label,
			description="This feed contains the " + str(count) + " most recent posts to " + community_label
		)
		
		return feed
	
	def get_top_community_posts_feed(self, request, community=None, count=None):
		
		if count is None:
			count = 25
		
		if community is None:
			path = "resources/votes/top/" + str(count)
			community_label = "any community"
		else:
			path = "resources/votes/community/" + community + "/top/" + str(count)
			community_label = community
		
		url = self.make_voting_url(request, path)
		# print("Voting url:", url)
		
		api_top_posts_scores = self.query_api(url)
		# print("Top posts scores:")
		# pprint.pprint(api_top_posts_scores)
		
		# Grab full info on each post and modify the title to include the score
		posts = list()
		for post_score in api_top_posts_scores:
		
			post = self.fetch_post(request, post_score["id"])
			
			post["title"] = "(" + str(post_score["score"]) + ") " + post["title"]
			
			posts.append(post)
		
		feed = self.posts_to_feed(
			posts,
			title="Top " + str(count) + " posts to " + community_label,
			description="This feed contains the " + str(count) + " top voted posts to " + community_label
		)
		
		return feed
	
	def get_hot_community_posts_feed(self, request, community=None, count=None):
		
		if count is None:
			count = 25
		
		if community is None:
			community_label = "any community"
		else:
			community_label = community
		
		# First we need to grab the X most recent posts to be considered,
		# using our sibling method
		# We will also use a "reasonably" limit for posts to examine.
		posts = self.get_recent_community_posts(
			request,
			community=community,
			count=self.__reasonable_hot_examination_limit
		)
		
		# We then pair each post with its Reddit "hot" ranking, using tuples:
		posts_ranked = list()
		for post in posts:
			
			post_datetime_object = self.database_date_to_datetime_object(post["date"])
			post_score_info = self.fetch_post_score(request, post["id"])
			
			post_ups = post_score_info["upvotes"]
			post_downs = post_score_info["downvotes"]
			
			post_hottness = Reddit.hot(post_ups, post_downs, post_datetime_object)
			post_ranked = (post, post_score_info, post_hottness)
			
			posts_ranked.append(post_ranked)
			
		# We then need to sort the posts using their ranking:
		posts_ranked_sorted = sorted(posts_ranked, reverse=True, key=lambda tup: tup[2])
		
		# We then pull the top "count" posts (should be in descending order by this time)
		# (and mess with the titles to the "hot" score, just for fun)
		posts_hot = list()
		for i in range(count):
			
			if i >= len(posts_ranked_sorted):
				break
			
			post, score_info, hotness = posts_ranked_sorted[i]
			
			post["title"] = "(" + str(score_info["score"]) + ") " + post["title"]
			post["title"] = "(" + str(hotness) + ") " + post["title"]
			
			posts_hot.append(post)
		
		# We can then convert them into a feed
		feed = self.posts_to_feed(
			posts_hot,
			title="Hottest " + str(count) + " posts to " + community_label,
			description="This feed contains the " + str(count) + " hottest posts in " + community_label
		)
		
		return feed
	
	def fetch_post(self, request_original, post_id):
		
		url = self.make_posting_post_url(request_original, post_id)
		
		data = self.query_api(url)
		
		return data
	
	def fetch_post_score(self, request_original, post_id):
		
		url = self.make_voting_post_score_url(request_original, post_id)
		
		data = self.query_api(url)
		
		return data
	
	def posts_to_feed(self, posts, title, description):
		
		items = list()
		for post_data in posts:
			
			post_id = post_data["id"]
			
			# Fetch each post so we can get at its text body
			post = self.fetch_post(request, post_id)
			
			item = rfeed.Item(title=post_data["title"])
			
			# Use the resource URL as the "link"
			if "resource_url" in post_data.keys():
				item.link = post_data["resource_url"]
			
			item.description = (
					"Post created by user " + post_data["username"]
					+ " on " + post_data["date"]
					+ " in " + post_data["community"]
					+ "\n"
					+ post["text"]
			)
			
			item.author = post_data["username"]
			
			# No url in original scheme, so just use global ID
			item.guid = rfeed.Guid(self.make_posting_post_url(request, post_id))
			
			# print(post_data)
			item.pubDate = self.database_date_to_datetime_object(post_data["date"])
			
			items.append(item)
		
		feed = rfeed.Feed(
			title=title,
			link=request.url,
			description=description,
			language="en-US",
			lastBuildDate=datetime.datetime.now(),
			items=items
		)
		
		return feed
	
	def query_api(self, url, method="GET", data=None):
		
		headers = None
		
		r = requests.get(url, headers=headers, timeout=self.__api_timeout)
		
		try:
			data = json.loads(r.content)
		except json.decoder.JSONDecodeError:
			print("query_api - Failed to decode json from " + url + ": \n" + str(r.content))
			return None
		
		return data
	
	@staticmethod
	def database_date_to_datetime_object(s):
		
		o = datetime.datetime.strptime(
			s,
			"%Y-%m-%d %H:%M:%S"
		)
		
		return o
