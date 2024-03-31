import json
import sys
import os

listdirs = os.listdir('data')
list_urls = []
for dir in listdirs:
    if (dir.endswith('.json')):
        with open('data/' + dir, 'r', encoding='utf-8') as f:
            data = json.load(f)
            list_urls.extend(data)

list_urls = list(map(lambda x: x.split('-jv?')[0], list_urls))
list_urls = list(set(list_urls))

with open('crawl_info/crawl_info/data/newurls.json', 'w', encoding='utf-8') as f:
    json.dump(list_urls, f, indent=4, default=str, ensure_ascii=False)