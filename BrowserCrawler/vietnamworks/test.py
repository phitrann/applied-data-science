# import re

# a = 'Hết hạn trong 26 ngày'

# b = re.search(r"\d+", a).group()
# print(b)

import datetime as dt

a = (dt.datetime.now() + dt.timedelta(days = 26)).strftime("%Y-%m-%d")
print(a)