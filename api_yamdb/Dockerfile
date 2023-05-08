FROM python:3.7-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r /app/requirements.txt --no-cache-dir

#RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY api_yamdb/ /app

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ] 