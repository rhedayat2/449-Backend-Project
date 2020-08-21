
# CPSC 449 - Project 2

Main repository for [CPSC 449, Group Project #2](https://docs.google.com/document/d/1c28RSlpJK9pUMkgvaFIt1e1Gi920cjYf3T5b-FbITQ0/edit)

## Team Members

* [Dev1] Upal Patel <upalpatel@csu.fullerton.edu>
* [Dev2] Rahin Hedayat <rhedayat2@csu.fullerton.edu>
* [Dev3] Mike Peralta <mikeperalta@csu.fullerton.edu>

## Professor Instructions

### Git Branch

Please make sure you're on the ***master*** branch.

### Start With the Main Menu

To begin testing this project, navigate to the *operations* folder and enter the following command:

```make```

We're using GNU Make as a simple collection of shortcuts, to make running our various setup scripts and commands less confusing.
It will also automatically record output of certain commands into the log folder.

### Commands of Interest

You're probably most interested in the following commands, run in the following sequence:

1. ```make reset```

	This will initialize the database

2. ```make foreman```

	This will start the production server with 3 processes per microservice (each with their own WSGI instance), and a Caddy process for load balancing.
	It will also block the terminal so you'll have to spawn or split a new one.

3. ```make populate```

	This will use the microservice APIs to populate the database with some test data.

4. ```make test-posting```

	This will further test the posting microservice API in much finer detail than population does.

5. ```make test-voting```

	This will further test the voting microservice API in much finer detail than population does.

Caddy will also write to a log file at *services/log/access.log*. You can start tail'ing it after foreman has launched.

### New BFF endpoints

You probably want to know the RSS feed endpoints. They become available after using steps 1-3 in the ***Commands of Interest*** section.

When run on localhost, they are:

* [The 25 most recent posts to a particular community](http://localhost:2015/rss/v1/resources/community/cats/recent)
* [The 25 most recent posts to any community](http://localhost:2015/rss/v1/resources/posts/recent)
* [The top 25 posts to a particular community, sorted by score](http://localhost:2015/rss/v1/resources/community/cats/top)
* [The top 25 posts to any community, sorted by score](http://localhost:2015/rss/v1/resources/posts/top)
* [The hot 25 posts to any community, ranked using Reddit's "hot ranking" algorithm](http://localhost:2015/rss/v1/resources/community/cats/hot)

### Potential Issues

As of this writing, we had to hardcode the API ports Caddy expects to load balance to:

* 5000-5099 are unused (Foreman assigns this port range to Caddy, but we've hard-coded its port to 2015 per assignment prompt)
* The /posts microservice gets ports 5100-5102
* The /votes microservice gets ports 5200-5202
* The /rss BFF service gets ports 5300-5302

## Installation Instructions

### Pip3 Requirements

The following pip3 requirements must be installed:

* flask_api
* python-dotenv
* requests
* rfeed

```
pip3 install --user Flask-API
pip3 install --user pip install python-dotenv
pip3 install --user pip install requests
pip3 install --user pip install rfeed
```

### Other Requirements

#### Foreman

Ruby-Foreman (debian repos)

Foreman is a process manager.
In this project, it will manage Gunicorn and Caddy processes for each microservice.

```bash
sudo apt install --yes ruby-foreman
```

#### GUnicorn3

GUnicorn (Web Service Gateway Interface aka ***WSGI***)

Note from prompt: *Be sure to run Gunicorn with the gunicorn3 command rather than gunicorn as shown in the
documentation.*

```bash
sudo apt install --yes gunicorn3
```

#### Caddy

Caddy is a simple web server that we can use as the main entry point for the end-user.
Caddy will receive a user's request, and use the incoming URL to decide which instance/port of each microservice to redirect to, with load balancing.

```bash
curl https://getcaddy.com | bash -s personal
```

#### Tee

The command ***tee*** is needed to write console output to the logs directory, for certain commands:

```bash
sudo apt install --yes tee #probably
```

### Database Initialization

Follow these steps to initialize the database

1. Navigate to the ***operations*** folder inside the main repo directory
2. Execute the command ```make``` to see menu options (the Makefile currently serves as shortcuts for commands and variables)
3. Execute the menu option to reset the database; Probably ```make reset```

### Database Population

Follow these steps to populate the database with data

1. Navigate to the ***operations*** folder inside the main repo directory
2. Spawn three terminal windows
3. In one of the windows, execute the command ```make``` to see menu options (the Makefile currently serves as shortcuts for commands and variables)
4. In the first window, launch a development instance of the posting microservice, probably with ```make start-posting-dev```
5. In the second window, launch a development instance of the voting microservice, probably with ```make start-voting-dev```
6. In the third window, launch the script to populate the microservices via their APIs, probably with ```make populate```

## Team Instructions

Team instructions in this section.

### How to start your development instances

I've made a shortcut for you. Go into the operations folder and execute:

```make```

From there you should see several choices to start development instances of your APIs.

Of particular note:

* ```make start-posting-dev``` Will start a development instance of the posts microservice
* ```make start-voting-dev``` Will start a development instance of the votes microservice

### Populating and Testing Your Development instances

This section contains information to help you know when your microservices are (probably) perfect.
I've written test scripts to populate and thoroughly test your APIs.
The tests will run and hopefully give you an idea where to next work (if a test fails).
If all tests succeed, you might be finished.

Please note that my tests assume you'll be using the same endpoints that are currently in the following stubs:

* *services/posting_app.py*
* *services/voting_app.py*

I put these stubs in place so I could finish my work for operations early.
If you would like to change an endpoint, just let me know in chat so I can adjust my test scripts.

#### Populating the Microservices

As of this writing, both microservices need to be functional to populate either of them.
The reasoning for this is that we're using FOREIGN KEY constraints that make it impossible to even use the votes microservice without corresponding entries in the posts microservice.

Therefore, the first things that should be worked on are creation endpoints.

Once both microservices have creation (POST) endpoints up and running, they can be populated with the following command:

```make populate```

Note that *both microservices* should be running before executing the population script.

#### Testing the Posts Microservice

Tests should be run only after both microservices have been populated.
To test the posts microservice, you'll first need to start a development instance with:

```make start-posting-dev```

After that, you can execute the following command:

```make test-posting-dev```

#### Testing the Votes Microservice

Tests should be run only after both microservices have been populated.
To test the votes microservice, you'll first need to start a development instance with:

```make start-voting-dev```

After that, you can execute the following command:

```make test-voting-dev```

### Git Strategy

Strategy for git usage.

#### Branching

All work should be done on the ***dev*** branch. When the project is in a stable state (i.e., it works), the ***dev*** branch will be merged into the ***master*** branch.

So when first cloning this repository, make sure you're starting on dev with the command:

```git checkout dev```

#### Tags

Whenever the project reaches a stable state that could be considered "the best turn-in-able state we have available", a git tag should be added.

Tags should follow the standard [Semantic Versioning](https://semver.org/) scheme (i.e., MAJOR.MINOR.PATCH).



