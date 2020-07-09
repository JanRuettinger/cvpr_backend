from flask import Flask
from flask import request
from elasticsearch import Elasticsearch
import json
from flask_cors import CORS, cross_origin
import pandas as pd
import time
import logging

time.sleep(12)

es = Elasticsearch('elasticsearch:9200') #es.indices.delete('my_index')

while True:
    try:
        es.search(index="")
        break
    except (
        elasticsearch.exceptions.ConnectionError,
        elasticsearch.exceptions.TransportError
    ):
        time.sleep(1)

# def seed():
#     try:
#         es.indices.delete('cvpr')
#     except:
#         print("Index already deleted.")

#     df = pd.read_csv("/app/cvpr_data_preprocessed.csv")

#     print("in seed data")

#     for index,row in df.iterrows():
#         title = row["title"]
#         abstract = row["abstract"]
#         authors = row["authors"]
#         authors = "; ".join(authors.split(";"))
#         institutions = row["institutions"]
#         institutions = "; ".join(institutions.split(";"))
#         url = row["url"]
#         es.index(index='cvpr', id=index, body={'title': title, 'abstract': abstract, 'authors': authors, 'institutions': institutions, 'url': url})
#     # print(counter)

#     print("Elastic Search successfully seeded with index: cvpr")

# seed()

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
    print(query_string_formatted)
    app.logger.debug("####### NEW QUERY ###########")
    app.logger.debug(f'Query string: {query_string}')
    app.logger.debug(f'Query location: {query_location}')
    

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
    
    # query = {
    #     "query": {
    #         "multi_match" : {
    #         "query" : query_string,
    #         "fields" : fields,
    #         "type": "phrase"
    #         }
    #     }
    # }

    result = es.search(index='cvpr', body=query, size=1800)
    result_formatted = []
    for i in result["hits"]["hits"]:
        dict_tmp = {"title": i["_source"]["title"], "abstract": i["_source"]["abstract"], "institutions": i["_source"]["institutions"], "authors": i["_source"]["authors"], "url": i["_source"]["url"] }
        result_formatted.append(dict_tmp)
    app.logger.debug(len(result_formatted))
    app.logger.debug("##########  ###########")
    dict_result = {"query": query_string, "result": result_formatted}
    return json.dumps(result_formatted)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)