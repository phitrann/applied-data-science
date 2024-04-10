import facebook_scraper as fs
import json
GROUP_ID = '5097678227028214'
POST_ID = '2141137466239921'
POST_URL = "https://www.facebook.com/groups/5097678227028214/?hoisted_section_header_type=recently_seen&multi_permalinks=7076413642487986"
MAX_COMMENTS = 10
# for i in range(1, 3):
#     fs.write_posts_to_csv(
#         group=5097678227028214, # The method uses get_posts internally so you can use the same arguments and they will be passed along
#         # post_urls = ["https://www.facebook.com/groups/5097678227028214/?hoisted_section_header_type=recently_seen&multi_permalinks=7076413642487986"],
#         page_limit=10,
#         timeout=60,
#         encoding ='utf8',
#         options={
#             'allow_extra_requests': False
#         },
#         cookies = 'cookies.json',
#         filename=f'data/messages_{i}.json', # Will throw an error if the file already exists
#         resume_file='next_page.txt', # Will save a link to the next page in this file after fetching it and use it when starting.
#         matching='.+', # A regex can be used to filter all the posts matching a certain pattern (here, we accept anything)
#         not_matching='^Warning', # And likewise those that don't fit a pattern (here, we filter out all posts starting with "Warning")
#         keys=[
#             'post_id',
#             'text',
#             'timestamp',
#             'time',
#             'user_id'
#         ], # List of the keys that should be saved for each post, will save all keys if not set
#         format='json', # Output file format, can be csv or json, defaults to csv
#         days_limit=3650 # Number of days for the oldest post to fetch, defaults to 3650
#     )
# cj = browser_cookie3.chrome(domain_name='.facebook.com')

# gen = fs.get_posts(
#             group=213587320199694, pages=4, options={"allow_extra_requests": False}, cookies = cj,
#         )

posts = fs.get_posts(
            group="174764463261090",pages=3, options={"allow_extra_requests": True}, cookies = "FacebookScraper/cookies.txt", days_limit = 1
        )

with open('post-comments.json', 'w', encoding='utf-8') as of:
    json.dump(list(posts), of, indent=4, default=str, ensure_ascii=False)