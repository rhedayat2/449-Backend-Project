-- :name post_by_id :one
SELECT post_id, upvotes, downvotes FROM vote
WHERE post_id = :post_id;