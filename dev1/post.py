from flask import Flask, request
from flask_api import FlaskAPI, status, exceptions
from flask_dynamo import Dynamo
import boto3
from boto3.dynamodb.conditions import Key, Attr
import postAPI

#Get the service resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")
#Get the client
client = boto3.client('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")

app = FlaskAPI(__name__)

@app.route("/posts")
def home():
    postAPI.new_table()
    return "<h1>Creating a new table</h1>"

@app.route("/posts/populate")
def populate_posts_table():

    postAPI.populate_posts()
    return { "status" : "posts table has been populated" }, status.HTTP_201_CREATED


#create a new post
@app.route("/posts/add", methods=["POST", "GET"])
def createPost():
    if request.method == "GET":
        return { "status": "ready to create post" }

    create = postAPI.create_post(**(request.data))
    if create is None:
        return { "status": "post created successfully"}, status.HTTP_201_CREATED
    else:
        return {"status": "could not create post"}, status.HTTP_500_INTERNAL_SERVER_ERROR

#get post by id
@app.route("/posts/id/<int:post_id>", methods=["GET"])
def getPostByID(post_id):
    get_post = postAPI.get_post(post_id)
    if get_post:
        return get_post
    else:
        return { "status" : "post not found" }, status.HTTP_204_NO_CONTENT

#get all posts
@app.route("/posts/all", methods=["GET"])
def getAllPosts():
    get_posts = postAPI.get_posts()
    return get_posts

#get n amount of recent posts
@app.route("/posts/<int:max_count>", methods=["GET"])
def nPosts(max_count):
    print("n entered: ", max_count)

    posts_list = postAPI.get_n_posts_list(max_count)
    if posts_list:
        return posts_list
    else:
        return { "status" : "recent posts not found" }, status.HTTP_204_NO_CONTENT

#get n amount of recent posts by community
@app.route("/posts/<int:max_count>/<string:Community>")
def nCommunityPosts(max_count, Community):
    print("n entered: ", max_count)
    print("Community entered: ", Community)

    community_posts_list = postAPI.get_community_posts_list(max_count, Community)
    if community_posts_list:
        return community_posts_list
    else:
        return { "status" : "recent community posts not found" }, status.HTTP_204_NO_CONTENT

#delete post by id
@app.route("/posts/delete/<int:post_id>", methods=["GET", "DELETE"])
def deletePost(post_id):
    print(""*100)
    print("post id entered: ", post_id)

    if request.method=="DELETE":
        postAPI.delete_post(post_id)
    else:
        return { "message": "Error - post not deleted yet" }, status.HTTP_400_BAD_REQUEST

#delete all posts
@app.route("/posts/delete/all", methods=["GET", "DELETE"])
def deletePosts():
    if request.method=="DELETE":
        postAPI.delete_posts()
    else:
        return { "message": "Error - posts not deleted yet" }, status.HTTP_400_BAD_REQUEST
