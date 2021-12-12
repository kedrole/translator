import requests
import json
from django.conf import settings

class YandexTranslate:
    def __init__(self):
        self.IAM_token = self.get_IAM_token(settings.YANDEX_OAUTH_TOKEN)

    def get_IAM_token(self, OAuth_token):
        ''' Получить IAM-токен по Oauth-токену'''
        data = '{"yandexPassportOauthToken":"' + OAuth_token + '"}'
        try:
            response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', data=data)
            return json.loads(response.text)['iamToken']
        except Exception as e:
            print("Ошибка получения IAM-токена")
            return ''

    def get_translation_list(self, original_list):
        ''' Получить список с переводом оригиналов из списка, подающегося на вход. Учесть ограничения переводчика в 10000 символов на 1 запрос '''
        result_list = []

        list_of_translation_lists_with_overall_textlength_less_10000 = self.get_list_of_text_lists_with_overall_textlength_less_10000(original_list)

        # DEBUG
        #sums = [sum([len(text) for text in lst]) for lst in list_of_translation_lists_with_overall_textlength_less_10000]
        #print("Суммы символов: ")
        #print(sums)

        for original_lst in list_of_translation_lists_with_overall_textlength_less_10000:
            (status, result) = self.get_translation(original_lst)
            if status == 'success':
                result_list.extend(result)
            else:
                return (status, result)
        return ('success', result_list)

    def get_list_of_text_lists_with_overall_textlength_less_10000(self, text_list):
        ''' Получить список списков текста с суммарной длиной фрагментов текста менее 10000 символов'''
        ret_list = []

        text_lenghts_sum = 0
        last_text_ind = 0

        for ind, text in enumerate(text_list):
            text_lenghts_sum += len(text)
            if text_lenghts_sum >= 9000:
                ret_list.append(text_list[last_text_ind:ind])
                last_text_ind = ind
                text_lenghts_sum = len(text)

        ret_list.append(text_list[last_text_ind:])
        return ret_list


    def get_translation(self, original):
        ''' Получить перевод текста списка оригиналов '''
        data = {
            "folderId": settings.YANDEX_FOLDER_ID,
            "texts": original,
            "sourceLanguageCode": "en",
            "targetLanguageCode": "ru"
        }

        headers = {"Authorization": "Bearer " + self.IAM_token}

        resp = None
        try:
            resp = requests.post("https://translate.api.cloud.yandex.net/translate/v2/translate", data=str(data).encode("utf-8"), headers=headers)
            print(resp.text)
        except Exception as e:
            return ("error", "Post error: " + str(e))
        try:
            results = [item["text"] if "text" in item else "" for item in json.loads(resp.text)['translations']]
            return ("success", results)
        except Exception as e:
            return ("error", "Get translation error: " + str(e) + ". " + resp.text)