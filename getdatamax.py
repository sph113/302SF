import json, requests

ordernumber=7
link="http://xnobe.synology.me:8080/ordersjson/"+str(ordernumber)
url = requests.get(link)
text = url.text

data = json.loads(text)

print(data)