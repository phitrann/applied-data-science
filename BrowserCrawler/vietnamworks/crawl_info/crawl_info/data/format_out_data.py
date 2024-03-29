'''
    Format lại dữ liệu sau khi thu thập để dễ dàng quan sát các lỗi.
    File out.json là các dữ liệu sau khi thu thập
    File newout.json là dữ liệu sau khi format lại
'''

import json

with open('data/info.json', 'r', encoding='utf8') as f:
    data = json.load(f)

with open('data/newout.json', 'w', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)