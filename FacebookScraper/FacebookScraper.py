import facebook_scraper as fs 
import json
import os

'''
    PostID có thể sử dụng cho một bài post của các cá nhân đăng bài công khai trên facebook, hoặc các bài post trong Public Group.
    GroupID để thu thập các bài post trong một Public Group một lần.
    Name để thu thập các post thuộc một cái tên được đề cập trên facebook (cách này khá phức tạp và cảm giác hơi phiền vì phải thêm nhiều trường để xác định)
'''

class FacebookScraper:
    def __init__(self, cookies = None):
        pass
    
    def Scrap_by_post(self, postID = None):
        if not postID:
            print("No postID is provided")
            return
        else:
            print(f"Scraping post {postID}")
            # get the post (this gives a generator)
            gen = fs.get_posts(
                post_urls=[postID],
                options={"comments": True, "progress": True, "allow_extra_requests": True},
                cookies= 'FacebookScraper/cookies.txt'
            )
            # take 1st element of the generator which is the post we requested
            post = next(gen)
            # # extract the comments part
            comments = post['comments_full']
            with open('data/postinfo.json', 'w', encoding='utf-8') as of:
                json.dump(post, of, indent=4, default=str, ensure_ascii=False)
            # process comments as you want...
            with open('data/comment.json', 'w', encoding='utf-8') as of:
                json.dump(comments, of, indent=4, default=str, ensure_ascii=False)
    
    def Scrap_by_group(self, groupID = None):
        posts = fs.get_posts(
            group=groupID,pages=3, options={"allow_extra_requests": True}, cookies = "FacebookScraper/cookies.txt", days_limit = 1
        )

        with open('data/group-post.json', 'w', encoding='utf-8') as of:
            json.dump(list(posts), of, indent=4, default=str, ensure_ascii=False)