FROM python:3.8-alpine

#RUN apk update && apk add vim 

RUN mkdir -p /var/www/picture
WORKDIR /var/www/picture
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# ENV PYTHONUNBUFFERED 1
COPY . .

ENTRYPOINT ["python","www/app.py"]
EXPOSE 8080