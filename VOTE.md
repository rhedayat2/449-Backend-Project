
# Voting Microservice

This file is documentation for the ***voting*** microservice.

For general project documentation/information, see the (README.md)[README.md] file

# Operations
To run the voting microservice:
    Enter operations folder and run: make start-voting-dev

## Upvote a Post

     Run:
         curl http://localhost:8001/votes/v1/resources/votes/<int:post_id>/upvote

## Downvote a Post

     Run:
         curl http://localhost:8001/votes/v1/resources/votes/<int:post_id>/downvote

## Report the number of upvotes and downvotes for a post

     Run:
         curl http://localhost:8001/votes/v1/resources/votes/<int:post_id>

## List the​ **n**​ top-scoring posts to any community

     Run:
         curl http://localhost:8001/votes/v1/resources/votes/top/<int:count>

## Given a list of post identifiers, return the list sorted by score

     Run:
         curl http://localhost:8001/votes/v1/resources/votes/sort
     
     For example:
        curl --header 'Content-Type: application/json' --data '{"post_id":[1,3,2]}' http://localhost:8001/votes/v1/resources/votes/sort



