# 
FROM python:3.10

# 
RUN mkdir /fastapi_app

# 
WORKDIR /fastapi_app

# 
COPY requirements.txt .

# 
RUN pip install -r requirements.txt

# 
COPY . .

#
WORKDIR app

# 
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=127.0.0.1:8000



