-- name:deletePost :affected
DELETE FROM post
WHERE id = :id;
