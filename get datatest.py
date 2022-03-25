import json, requests



link="http://xnobe.synology.me:8080/ordersjson"
url = requests.get(link)
text = url.text
data = json.loads(text)
print(data)

iterdata = iter(data)
next(iterdata)
for i in iterdata:
    number=i
    link2="http://xnobe.synology.me:8080/ordersjson/"+number.replace('order','')
    url2 = requests.get(link2)
    text2 = url2.text
    data2 = json.loads(text2)
    print(data2)