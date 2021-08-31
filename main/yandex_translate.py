import requests
import json
from django.conf import settings

class YandexTranslate:
    def __init__(self):
        pass

    def get_IAM_token(self, OAuth_token):
        data = '{"yandexPassportOauthToken":"' + OAuth_token + '"}'
        try:
            response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', data=data)
            return json.loads(response.text)['iamToken']
        except Exception as e:
            print("Ошибка получения IAM-токена")
            return ''

    def get_translation_list(self, original_list):
        data = {
            "folderId": settings.YANDEX_FOLDER_ID,
            "texts": original_list,
            "sourceLanguageCode": "en",
            "targetLanguageCode": "ru"
        }

        headers = {"Authorization": "Bearer " + self.get_IAM_token(settings.YANDEX_OAUTH_TOKEN)}
        try:
            resp = requests.post("https://translate.api.cloud.yandex.net/translate/v2/translate", data=str(data).encode("utf-8"), headers=headers)
            print(resp.text)
            results = [item["text"] for item in json.loads(resp.text)['translations']]
            return ("success", results)
        except Exception as e:
            return ("error", str(e))