-- :name createPost :insert
INSERT INTO post(`title`, `text`, `community`, `username`)
VALUES (:title, :text, :community, :username);
