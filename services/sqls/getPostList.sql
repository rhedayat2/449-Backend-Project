-- :name getPostList :many
SELECT `id`, `date`, `title`, `community`, `username`
FROM post
WHERE community = :community
ORDER BY date DESC;
