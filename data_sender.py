import requests

API_ENDPOINT = "http://127.0.0.1:5000/new_touch_data"

data = {'user_id' : 1, 'eqnt_id' : 1, 'set_busy' : 0}

r = requests.post(url = API_ENDPOINT, data = data)

ret = r.text
print("return is :%s"%ret)
