"""
Download comments for a public Facebook post.
"""

import facebook_scraper as fs
import json

# get POST_ID from the URL of the post which can have the following structure:
# https://www.facebook.com/USER/posts/POST_ID
# https://www.facebook.com/groups/GROUP_ID/posts/POST_ID
POST_ID = "pfbid0E3VbbfToKC8FLuXVGiVu5exRnyj1R25zDknVs6Xr8tzBMhmrDFw94g1ne95qWPiWl"

# number of comments to download -- set this to True to download all comments
MAX_COMMENTS = 10

# get the post (this gives a generator)
gen = fs.get_posts(
    post_urls=[POST_ID],
    options={"comments": MAX_COMMENTS, "progress": True},
    cookies= 'facebook-scraper/cookies.txt'
)

# take 1st element of the generator which is the post we requested
post = next(gen)
# # extract the comments part
comments = post['comments_full']

with open('facebook-scraper/postinfo.json', 'w', encoding='utf-8') as of:
    json.dump(post, of, indent=4, default=str, ensure_ascii=False)

# process comments as you want...
with open('facebook-scraper/comment.json', 'w', encoding='utf-8') as of:
    json.dump(comments, of, indent=4, default=str, ensure_ascii=False)