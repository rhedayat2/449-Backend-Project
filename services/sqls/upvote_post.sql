-- :name upvote_post :affected
UPDATE vote
SET upvotes = upvotes + 1
WHERE post_id = :post_id;