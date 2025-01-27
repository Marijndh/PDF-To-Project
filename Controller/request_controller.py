import os

from dotenv import load_dotenv, set_key, find_dotenv

from Entity.Token import Token
from Entity.request import Request

load_dotenv()


class RequestController:
    def __init__(self):
        self.api_url = os.getenv("API_URL")
        self.api_key = os.getenv("API_KEY")
        self.token = os.getenv("API_TOKEN")
        self.app_name = os.getenv("APPLICATION_NAME")
        if self.token == '': self.get_token()

    def get_token(self):
        request = Request(self.api_url, self.token)
        response = request.post(f'/auth/login/{self.app_name}/apiKey?apiKey={self.api_key}', {})
        token = Token(**response.json())
        self.token = token.value
        print(self.token)
        set_key(find_dotenv(), "API_TOKEN", token.value)

    def create_project(self, project):
        request = Request(self.api_url, self.token)
        response = request.post('/project', project)
        return response
