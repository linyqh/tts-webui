import requests


# 判断是否为有效的url
def is_valid_url(url):
    try:
        response = requests.head(url + '/docs')
        return response.status_code == 200
    except:
        return False
