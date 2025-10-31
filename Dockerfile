FROM python:3.13-slim


RUN apt-get update && apt-get install -y nginx


WORKDIR /app


COPY . /app


RUN pip install --upgrade pip && pip install -r requirements.txt
RUN chmod -R 755 /data/media

COPY nginx.conf /etc/nginx/nginx.conf


COPY start.sh /start.sh
RUN chmod +x /start.sh


EXPOSE 8000

CMD ["/start.sh"]