import os
import requests
import json
from django.conf import settings

class UniqueCheck:
    def __init__(self):
        self.session = requests.Session()
        self.userkey = settings.TEXT_RU_KEY

    def send_text_and_get_uid(self, text, exceptdomain):
        try:
            url = "http://api.text.ru/post"
            
            data = {
                "text": text,
                "userkey": self.userkey,
                "exceptdomain": exceptdomain,
                "copying": "noadd",
            }

            a = requests.post(url, data=data, verify=False)
            js = json.loads(a.text)
            print(js)
            uid=js["text_uid"]
            return {"status": "success", "uid": uid}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_result(self, uid):
        url = "http://api.text.ru/post"

        data = {
            "uid": uid,
            "userkey": self.userkey,
        }
        try:
            a = requests.post(url, data=data, verify=False)
            js = json.loads(a.text)

            if "result_json" in js:
                js = json.loads(js["result_json"])
                return {"status": "success", "result": js}

            if "error_code" in js:
                if int(js["error_code"]) == 181:
                    return {"status": "not-checked", "message": js}
                return {"status": "error", "message": js}

        except Exception as e:
            return {"status": "error", "message": "Exception: " + str(e)}


'''
            date_check = js["date_check"]
            unique = js["unique"]
            urls = js["urls"]
            print(urls[1]['plagiat'])
            print(urls[1]['url'])
            print(date_check)
            print(unique)
            print(urls)

# ERROR
            print(js["error_code"])
            print(js["error_desc"])
'''