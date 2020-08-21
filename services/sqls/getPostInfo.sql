-- :name postInfo :many
SELECT `id`, `date`, `title`, `community`, `username`, `resource_url`
FROM post
WHERE id = :id;
