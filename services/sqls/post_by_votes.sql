-- :name post_by_votes :many
SELECT post_id, upvotes, downvotes FROM vote
ORDER BY upvotes - downvotes DESC
LIMIT :count;