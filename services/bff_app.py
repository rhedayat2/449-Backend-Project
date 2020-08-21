

from BFF import BFF

import flask
from flask import request
from flask_api import FlaskAPI, status


import os

#
api_prefix = "/rss/v1/"


# Instantiate the flask API
app = FlaskAPI(__name__)
app.config.from_envvar('APP_CONFIG')


# Instantiate the BFF helper class
bff = BFF("BFF", app, api_prefix)
if "FLASK_ENV" in os.environ and os.environ["FLASK_ENV"] == "development":
	bff.set_development_mode(True)


"""
Just for routing; Real functionality is inside BFF.py class
"""


def respond_with_feed(feed):
	
	response: flask.Response = flask.make_response()
	
	response.headers["Content-Type"] = "application/rss+xml"
	response.data = feed.rss()
	
	return response


@app.route("/")
def home():
	return "<h1>BFF API</h1><p>See our documentation .... somewhere</p>"


# Recent posts to any community
@app.route(api_prefix + "resources/posts/recent")
def bff_any_community_recent():
	
	if request.method == "GET":
		
		feed = bff.get_recent_community_posts_feed(request, community=None)
		
		return respond_with_feed(feed)
	
	return bff.error("Invalid method")


# Recent posts to a particular community
@app.route(api_prefix + "resources/community/<string:community>/recent")
def bff_particular_community_recent(community):
	
	if request.method == "GET":
		
		feed = bff.get_recent_community_posts_feed(request, community)
		
		return respond_with_feed(feed)
	
	return bff.error("Invalid method")


# The top 25 posts to any community, sorted by score
@app.route(api_prefix + "resources/posts/top")
def bff_any_community_top():
	
	if request.method == "GET":
		
		feed = bff.get_top_community_posts_feed(request, community=None)
		
		return respond_with_feed(feed)
	
	return bff.error("Invalid method")


# The top 25 posts to a particular community, sorted by score
@app.route(api_prefix + "resources/community/<string:community>/top")
def bff_particular_community_top(community):
	
	if request.method == "GET":
		
		feed = bff.get_top_community_posts_feed(request, community)
		
		return respond_with_feed(feed)
	
	return bff.error("Invalid method")


# The hot 25 posts to a particular community, ranked using ​ Reddit’s “hot ranking” algorithm
@app.route(api_prefix + "resources/community/<string:community>/hot")
def bff_particular_community_hot(community):
	
	if request.method == "GET":
		
		feed = bff.get_hot_community_posts_feed(request, community)
		
		return respond_with_feed(feed)
	
	return bff.error("Invalid method")




