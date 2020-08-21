from Voting import Voting

from flask import request, jsonify
from flask_api import FlaskAPI, status
import sqlite3
import redis

app = FlaskAPI(__name__)
app.config.from_envvar('APP_CONFIG')

r = redis.Redis(host='localhost', decode_responses=True)

voting = Voting("Voting", app)

api_prefix = "/votes/v1/"

#created some posts
r.sadd("votes",1,2,3,4,5)
r.hset(1,"post_id",1)
r.hset(1,"upvotes",15)
r.hset(1,"downvotes",1)
r.hset(1, "total", int(r.hget(1,"upvotes")) - int(r.hget(1,"downvotes")))
r.hset(2,"post_id",2)
r.hset(2,"upvotes",110)
r.hset(2,"downvotes",23)
r.hset(2, "total", int(r.hget(2,"upvotes")) - int(r.hget(2,"downvotes")))
r.hset(3,"post_id",3)
r.hset(3,"upvotes",55)
r.hset(3,"downvotes",2)
r.hset(3, "total", int(r.hget(3,"upvotes")) - int(r.hget(3,"downvotes")))
r.hset(4,"post_id",4)
r.hset(4,"upvotes",6)
r.hset(4,"downvotes",1)
r.hset(4, "total", int(r.hget(4,"upvotes")) - int(r.hget(4,"downvotes")))
r.hset(5,"post_id",12)
r.hset(5,"upvotes",5)
r.hset(5,"downvotes",200)
r.hset(5, "total", int(r.hget(5,"upvotes")) - int(r.hget(5,"downvotes")))


@app.route("/votes")
def home():
	return "<h1>Voting API Root</h1><p>See our documentation .... somewhere</p>"

#upvote
@app.route(api_prefix + "resources/votes/<int:post_id>/upvote", methods=["GET"])
def up_vote(post_id):
	#check if post exists
	post = r.hexists(post_id, "upvotes")
	if post:
		#updates upvotes and total with hincrby function
		r.hincrby(post_id, "upvotes", 1)
		r.hincrby(post_id, "total", 1)
		return { 'message': 'upvoted post'}, status.HTTP_200_OK
	else:
		return { 'message': 'Post Does Not Exist' }, status.HTTP_400_BAD_REQUEST


#downvote
@app.route(api_prefix + "resources/votes/<int:post_id>/downvote", methods=["GET"])
def down_vote(post_id):
	#check if post exists
	post = r.hexists(post_id, "downvotes")
	if post:
		#updates upvotes and total with hincrby function
		r.hincrby(post_id, "downvotes", 1)
		r.hincrby(post_id, "total", -1)
		return { 'message': 'downvoted post'}, status.HTTP_200_OK
	else:
		return { 'message': 'Post Does Not Exist' }, status.HTTP_400_BAD_REQUEST



#Report the number of upvotes and downvotes for a post
@app.route(api_prefix + "resources/votes/<int:post_id>", methods=["GET"])
def get_votes(post_id):
	#check if post exists
	post = r.hexists(post_id, "post_id")
	if post:
		#returns all the info of the post
		return r.hgetall(post_id), status.HTTP_200_OK
	else:
		return { 'message': 'Post Does Not Exist' }, status.HTTP_400_BAD_REQUEST



# List the top voted posts of any community
@app.route(api_prefix + "resources/votes/top/<int:count>", methods=["GET"])
def votes_posts_top(count=None):
	num = r.scard("votes")
	if(count > num):
		return { 'message': 'Not enough posts exist' }, status.HTTP_400_BAD_REQUEST
	else:
		#sort using redis sort function
		list1 = r.sort("votes", by="*->total", desc=True)
		list2 = []
		for i in range(count):
			Pid = int(list1[i])
			list2.append(Pid)
		return list2, status.HTTP_200_OK

		


# Sort a list of post IDs by their vote scores
@app.route(api_prefix + "resources/votes/sort", methods=["GET", "POST"])
def votes_sort_posts():
	#request the post_ids
	list1 = request.json["post_id"]
	count = len(list1)
	list2 = []
	for i in list1:
		if(r.hexists(i, "post_id")):
			tot = r.hget(i, "total")
			r.sadd("temp", i)
			r.hset(i, "total", tot)
			list2 = r.sort("temp", by="*->total", desc=True)
			

		else:
			return { 'message': 'Error' }, status.HTTP_400_BAD_REQUEST
	r.delete("temp")
	
		
	return list2, status.HTTP_200_OK
		
