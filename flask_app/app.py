from flask import Flask
from flask import request
from elasticsearch import Elasticsearch
import json
from flask_cors import CORS, cross_origin


# es = Elasticsearch('http://localhost:9200') #es.indices.delete('my_index')

# while True:
#     try:
#         es.search(index="")
#         break
#     except (
#         elasticsearch.exceptions.ConnectionError,
#         elasticsearch.exceptions.TransportError
#     ):
#         time.sleep(1)


app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/search", methods = ['POST'])
@cross_origin(supports_credentials=True)
def search_all():
    print(request.get_json())
    data = request.get_json()
    query_string = data['query']
    query_location = data['location']

    fields = []
    if "i" in query_location:
        fields.append("institutions")
    if "a" in query_location:
        fields.append("authors")
    if "t" in query_location:
        fields.append("title")
    if "s" in query_location:
        fields.append("abstract")

    query_words = query_string.split()
    query_string_formatted = ""
    for word in query_words:
        query_string_formatted += f'*{word}* '

    if len(fields) == 0:
        fields = [""]
    print(fields)
    query = {
        "query":{
            "bool":{
                "must":[
                    {
                        "query_string":{
                            "query": query_string_formatted,
                            "fields": fields,
                            "default_operator":"and",
                        }
                    }]
            }
        }
    }

    result = es.search(index='cvpr', body=query, size=1800)
    result_formatted = []
    for i in result["hits"]["hits"]:
        dict_tmp = {"title": i["_source"]["title"], "abstract": i["_source"]["abstract"], "institutions": i["_source"]["institutions"], "authors": i["_source"]["authors"], "url": i["_source"]["url"] }
        result_formatted.append(dict_tmp)
    return json.dumps(result_formatted)

if __name__ == "__main__":
    app.run(host='0.0.0.0')