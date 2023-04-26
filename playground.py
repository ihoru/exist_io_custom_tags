#!/usr/bin/env python

from exist import *

# get('/users/$self/today/')
# params = dict(
#     limit='1',
#     groups='custom',
#     # date_max=date.today().strftime('%Y-%m-%d'),
# )
# response = get('/users/$self/attributes/', params=params)
# attributes = response.json()
# for attribute in attributes:
#     print(attribute['attribute'])
# grouped = OrderedDefaultDict(list)
# for attribute in attributes:
#     if attribute['attribute'] == 'custom':
#         continue
#     value = attribute['values'].pop(0)['value']
#     if not value:
#         continue
#     label_parts = attribute['label'].split(maxsplit=1)
#     key = label_parts[0]
#     if len(label_parts) == 1:
#         grouped[key] = value
#     else:
#         name = label_parts[1]
#         grouped[key].append(name)
# # sorting
# for key, values in grouped.items():
#     if isinstance(values, list):
#         grouped[key] = list(sorted(values))
# pprint(grouped)


data = [
    dict(value='good_meditate', date='2019-12-31'),
]
# post('/attributes/custom/append/', json=data)
print(get('/attributes/with-values/').text)
