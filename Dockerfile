FROM python:3.9 

WORKDIR /app

ADD .index/ .

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD *.py .
ADD bot bot/

ENV VECTOR_INDEX_FILE_LIST="asa_public_doc_index.json;asa_wiki_vector_index.json"

CMD ["python", "web.py"] 
EXPOSE 3978
