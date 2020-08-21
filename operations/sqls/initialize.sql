

-- Each posting should have a title, text, a community (​ subreddit​ ),
-- an optional URL linking to a resource (e.g. a news article or picture),
-- a username, and a date the post was made.
DROP TABLE IF EXISTS [post];
CREATE TABLE [post] (
	[id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	[date] DATETIME DEFAULT CURRENT_TIMESTAMP,
	[title] TEXT NULL,
	[text] TEXT NULL,
	[community] TEXT NULL,
	[resource_url] TEXT NULL,
	[username] TEXT NULL
);

-- Index on community for aggregate stuffs
CREATE INDEX [post__community] ON [post] (
	`community` ASC
);

-- Index to get recent community posts (???)
CREATE INDEX [post__date_community] ON [post] (
	`date` DESC,
	`community` ASC
);


-- Making up a schema that hopefully makes sense for voting
DROP TABLE IF EXISTS [vote];
CREATE TABLE [vote] (

	[id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	[date] DATETIME DEFAULT CURRENT_TIMESTAMP,
	[post_id] INTEGER NOT NULL,
  	[upvotes] INTEGER NOT NULL,
  	[downvotes] INTEGER NOT NULL,
	[username] TEXT NULL,

	-- https://sqlite.org/foreignkeys.html
	FOREIGN KEY (post_id) REFERENCES post(id)
);
-- Index to help grab total votes of posts
CREATE INDEX [vote__postID] ON [vote] (
	`post_id` ASC
);











