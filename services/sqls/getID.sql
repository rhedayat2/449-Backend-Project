-- :name getID :one
SELECT id, title, community, username, `date` FROM post
WHERE id = :id;
