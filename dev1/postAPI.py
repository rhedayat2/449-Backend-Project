import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

#Get the service resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")
#Get the client
client = boto3.client('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")

#create a new DynamoDB table
def new_table():
    newTable = dynamodb.create_table(
        TableName='posts',
        KeySchema=[
            {
                'AttributeName': 'post_id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'post_id',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 50,
            'WriteCapacityUnits': 50
        }
    )

    #wait until the table exists
    newTable.meta.client.get_waiter('table_exists').wait(TableName='posts')

#initialize posts table with 50 posts
#source: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.02.html
def populate_posts():

    params = create_post('User-1', 'Title-1', 'Some-text-1', 'odd', 'www.resource-url-1.com')
    num = 2
    for i in range(0,50):
        if i % 2 == 0:
            params = create_post('User-' + str(num), 'Title-' + str(num), 'Some-text-' + str(num), 'even', 'www.resource-url-' + str(num) + '.com')
        else:
            params = create_post('User-' + str(num), 'Title-' + str(num), 'Some-text-' + str(num), 'odd', 'www.resource-url-' + str(num) + '.com')
        num += 1

#create a new post
def create_post(username, title, text, community, resource_url):

    #current_post_id = 0
    #last_post_id = 0

    #find the table size by counting items
    load_table = dynamodb.Table('posts')
    table_size = load_table.item_count

    #set post IDs
    if table_size == None:
        last_post_id = 0
    else:
        posts_arr = get_posts() #returns an array of posts
        last_post_id = 1

        for post in posts_arr:
            if post['post_id'] > last_post_id:
                last_post_id = post['post_id']
    current_post_id = last_post_id + 1

    #what each post contains:
    parameters = {
        'post_id': current_post_id,
        'Username': str(username),
        'Title': str(title),
        'Text': str(text),
        'Community': str(community),
        'Resource_URL': str(resource_url)
    }

    #create table and add parameter items
    newTable = dynamodb.Table('posts')
    newTable.put_item(Item=parameters)

    return parameters

#retrieve an existing post
def post_exists(post_id):

    load_table = dynamodb.Table('posts')

    #using get_item since we only want a single post
    #alternatively, we can use querying or scanning
    #and return the first item found
    response = load_table.get_item(
        Key={'post_id': post_id}
    )

    post_found = response['Item']
    if post_found:
        return post_found
    else:
        return None

#get a post
def get_post(post_id):

    find_post = post_exists(post_id)
    if find_post==None:
        return { "status" : "the post does not exist" }
    else:
        return find_post

#get all posts, returns an array containing posts
#source: https://stackoverflow.com/questions/36780856/complete-scan-of-dynamodb-with-boto3
def get_posts():

    load_table = dynamodb.Table('posts')

    response = load_table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = load_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    sorted_data = sorted(data, key=lambda x: x['post_id'])
    return sorted_data

#list the n most recent posts by any community
def get_n_posts_list(max_count):

    load_table = dynamodb.Table('posts')
    table_size = load_table.item_count
    total = table_size - 1

    all_posts = get_posts()

    n_posts_list = []

    i = 0
    while i < max_count:
        n_posts_list.append(all_posts[total])
        i += 1
        total -= 1

    return n_posts_list

#list the n most recent posts by community
def get_community_posts_list(max_count, community):

    load_table = dynamodb.Table('posts')

    #filter data based on community
    response = load_table.scan(
        FilterExpression=Attr('Community').eq(community)
    )
    items = response['Items']
    total_posts_matches = len(items) - 1

    posts_list = []

    i = 0
    while i < max_count:
        posts_list.append(items[total_posts_matches])
        i += 1
        total_posts_matches -= 1

    return posts_list

#delete an existing post
def delete_post(post_id):

    find_post = post_exists(post_id)

    if find_post==None:
        return { "status" : "the post does not exist" }, status.HTTP_204_NO_CONTENT
    else:
        find_post.delete_item(Key={'post_id':post_id})
        return { "status" : "post deleted successfully" }


#drop posts table - deletes all posts in the table
#source: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.client.run-application-python.06-delete-table.html
def delete_posts():

    drop_table = dynamodb.Table('posts')
    drop_table.delete()

    #wait for the table to be deleted
    waiter = client.get_waiter('table_not_exists')
    waiter.wait(TableName='posts')

    return { "status" : "posts table deleted successfully" }
