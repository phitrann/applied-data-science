import json
import os
import datetime

with open('crawl_info/crawl_info/data/urls.json', 'r', encoding='utf-8') as f:
    urls = json.load(f)
    split_urls = list(map(lambda x: x.split('-jv?')[0], urls))
listdirs = os.listdir('data')
list_urls = [dir for dir in listdirs if dir.endswith('.json')]

with open(f'data/{list_urls[-1]}', 'r', encoding='utf-8') as f:
    latest_urls = json.load(f)
    

not_exist_urls = [url for url in latest_urls if url.split('-jv?')[0] not in split_urls]
urls.extend(not_exist_urls)

timenow = str(datetime.datetime.now().strftime("%Y-%m-%d"))
newpath = 'crawl_info/crawl_info/data/' + timenow + '.json'  
with open(newpath, 'w', encoding='utf-8') as of:
    json.dump(not_exist_urls, of, indent=4, default=str, ensure_ascii=False)
with open('crawl_info/crawl_info/data/urls.json', 'w', encoding='utf-8') as f:
    json.dump(urls, f, indent=4, default=str, ensure_ascii=False)
