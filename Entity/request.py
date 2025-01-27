import requests

class Request:
    def __init__(self, url, token):
        self._url= url
        self._token = token

    def set_token(self, token):
        self._token = token

    def prepare(self, endpoint):
        url = f'{self._url}{endpoint}'

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._token}'
        }
        return url, headers

    def get(self, endpoint):
        url, headers = self.prepare(endpoint)
        return requests.get(url, headers=headers)

    def post(self, endpoint, data):
        url, headers = self.prepare(endpoint)
        return requests.post(url, headers=headers, data=data)


