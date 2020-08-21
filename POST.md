
# Posting Microservice

This file is documentation for the ***posting*** microservice.

For general project documentation/information, see the (README.md)[README.md] file

## Steps to run:
```
flask run
```
```
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
```
```
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

## Create a New DynamoDB Table
```
http://localhost:5000/posts
```

## Populate the DynamoDB Table
```
http://localhost:5000/posts/populate
```

## Create a New Post
```
http://localhost:5000/posts/add
```

## Get Post by ID
```
http://localhost:5000/posts/id/<int:post_id>
```

## Get All Posts
```
http://localhost:5000/posts/all
```

## Get Recent Posts from Any Community
```
http://localhost:5000/posts/<int:n>
```

## Get Recent Posts by community
```
http://localhost:5000/posts/<int:n>/<string:community>
```

## Delete Post by ID
```
http://localhost:5000/posts/delete/<int:pos_id>
```

## Delete All Posts
```
http://localhost:5000/posts/delete/all
```
