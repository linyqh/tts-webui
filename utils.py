import requests


# 判断是否为有效的url
def is_valid_url(url):
    try:
        response = requests.head(url)
        print(response.status_code)
        return response.status_code == 200 or response.status_code == 404
    except:
        return False
