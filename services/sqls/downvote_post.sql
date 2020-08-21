-- :name downvote_post :affected
UPDATE vote
SET downvotes = downvotes + 1
WHERE post_id = :post_id;