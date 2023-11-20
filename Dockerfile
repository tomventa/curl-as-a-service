# Development api Dockerfile
FROM python:3.12

WORKDIR /code

COPY app/requirements.txt /code/app/requirements.txt
RUN pip install --no-cache-dir -r /code/app/requirements.txt

COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--header", "server:Digitamo/1.2"]
