
from MicroserviceBase import MicroserviceBase

from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

import sqlite3


class Posting(MicroserviceBase):

    def __init__(self, logName, app: FlaskAPI):

        self.__app = app

        super().__init__(logName, app)

    #Create a New Post
    def create_post(self, title, text, community, username, resource_url):

        parameters = {
            "title": title,
            "text": text,
            "community": community,
            "username": username,
            "resource_url": resource_url
        }

        print(parameters)

        new_post = self.query("createPost.sql", parameters)

        if new_post==None:
            print("post created")
        else:
            print("error creating post?")

        return new_post

    #Retrieve an Existing Post
    def post_exists(self, post_id):

        params = {
            "id": post_id
        }

        post = self.query("getPostInfo.sql", params)
        if post:
            return post
        else:
            return None

    #Delete an Existing Post
    def delete_post(self, post_id):

        params = {
            "id": post_id
        }

        delete = self.query("deletePost.sql", params)

        if delete:
            return { "status": "post deleted successfully" }
        else:
            return None

    #List the n most recent posts to a particular or any community
    def get_posts_list(self, community):

        params = {
            "community": community,
            #"max_count": max_count
        }

        rows = self.query("getPostList.sql", params)

        if rows==None:
            print("found posts")
        else:
            print("error finding posts?")

        return rows
