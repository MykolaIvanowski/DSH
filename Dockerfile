FROM python:3.13-slim


RUN apt-get update && apt-get install -y nginx


WORKDIR /app


COPY . /app


RUN pip install --upgrade pip && pip install -r requirements.txt

COPY nginx.conf /etc/nginx/nginx.conf


COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
EXPOSE 80

CMD ["/start.sh"]