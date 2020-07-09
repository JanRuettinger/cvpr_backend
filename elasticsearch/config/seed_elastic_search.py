from elasticsearch import Elasticsearch
import pandas as pd

es = Elasticsearch('http://localhost:9200')
df = pd.read_csv("/home/jan/cvpr_backend/elasticsearch/config/cvpr_data_preprocessed.csv")

try:
    es.indices.delete('cvpr')
except:
    print("Index already deleted.")


for index,row in df.iterrows():
    title = row["title"]
    abstract = row["abstract"]
    authors = row["authors"]
    authors = "; ".join(authors.split(";"))
    institutions = row["institutions"]
    institutions = "; ".join(institutions.split(";"))
    url = row["url"]
    es.index(index='cvpr', id=index, body={'title': title, 'abstract': abstract, 'authors': authors, 'institutions': institutions, 'url': url})
# print(counter)

print("Elastic Search successfully seeded with index: cvpr")
