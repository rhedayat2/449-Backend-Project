-- :name postExists :many
SELECT id FROM post
WHERE id = :id;
