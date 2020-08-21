
from Posting import Posting

import flask
from flask import request
from flask_api import FlaskAPI, status


# Instantiate the flask API
app = FlaskAPI(__name__)
app.config.from_envvar('APP_CONFIG')

posting = Posting("Posting", app)


"""
Just for routing; App/Data functionality is inside Posting.py class
"""

api_prefix = "/posts/v1/"


@app.route("/posts")
def home():
	return "<h1>Posting API Root</h1><p>See our documentation .... somewhere</p>"


# Get posts or create a new one
@app.route(api_prefix + "resources/posts", methods=["POST", "GET"])
def createPost():
    if request.method == "GET":
        return { "status": "ready to create post" }

    create = posting.create_post(**(request.data))
    if create is None:
        return { "status": "post created successfully"}
    else:
        return {"status": "could not create post"}, status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route(api_prefix + "resources/community/<string:community>/posts", methods=["GET"])
def posts(community=None):
    getPosts = posting.get_posts_list(community)
    if getPosts:
        return getPosts
    else:
        return {"status": "could not get posts"}, status.HTTP_500_INTERNAL_SERVER_ERROR

# Get a post
@app.route(api_prefix + "resources/post/<int:post_id>", methods=["GET"])
def one_post(post_id):

    # delete post if it exists
    getPost = posting.post_exists(post_id)
    if getPost:
        return getPost
    else:
        return { 'message': 'Error' }, status.HTTP_400_BAD_REQUEST

# Delete post if it exists
@app.route(api_prefix + "resources/post/delete/<int:post_id>", methods=["GET", "DELETE"])
def deletePost(post_id):

    if request.method=="DELETE":
        delete = posting.delete_post(post_id)

        if delete == 0:
            raise exceptions.NotFound()
        else:
            return '', status.HTTP_204_NO_CONTENT
    else:
        return {'status': 'OK'}
