import requests
import json
import base64

class Publish:
	def __init__(self):
		pass

	def post_article_to_site(self, site, token, title, content, date=None, status=None, categoryIdList=None, tagIdList=None):
		url = "https://" + site + "/wp-json/wp/v2/posts"

		user = "admin"
		password = ""
		credentials = user + ':' + password
		#token = base64.b64encode(credentials.encode())


		headers = {
			"Authorization": "Bearer %s" % token,
			"Content-Type": "application/json",
			"Accept": "application/json",
		}

		data = {
			'title': title,
			'content': content,
			'status': 'publish'
		}

		if date:
			data['date'] = date
			#"date": '2020-08-17T10:16:34',

		if status:
			data['status'] = status
			#"status": 'publish', # 'draft'

		if tagIdList:
			data['tags'] = tagIdList # [1367, 13224, 13225, 13226]

		if categoryIdList:
			data['categories'] = categoryIdList # [1374]
		print(data)
		response = None
		try:
			response = requests.post(url, headers=headers, json=data)
		except Exception as e:
			return {"success": False, "message": "Ошибка post запроса: " + str(e)}

		try:
			href = json.loads(response.text)['_links']["self"][0]['href']
			return {"success": True, "href": href}
		except Exception as e:
			return {"success": False, "message": "Ошибка json ответа: " + str(e) + ", response: " + response.text}


	def get_token(self):
		user = 'admin'
		password = 'Maezakmi77'

		credentials = user + ':' + password

		token = base64.b64encode(credentials.encode())

		data = {
			'username': user,
			'password':password
		}

		resp = json.loads(requests.post(token_url, data=data).text)
		if 'token' not in resp:
			print(resp)
			exit(0)

		token = resp['token']
		print(token)

