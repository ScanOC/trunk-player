FROM python:3.6 
RUN apt-get update && \
    apt-get -y install nginx redis-server tzdata && \
    rm -rf /var/lib/apt/lists/* 

RUN mkdir -p /app/trunkplayer
WORKDIR /app/trunkplayer

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
ADD requirements.txt /app/trunkplayer
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /var/log/trunk-player/

# copy project
#COPY . .
ADD . /app/trunkplayer
RUN rm -f /etc/nginx/sites-enabled/default
COPY trunk_player/trunk_player.nginx.docker /etc/nginx/conf.d/nginx.conf


ENTRYPOINT ["./entrypoint.sh"]

