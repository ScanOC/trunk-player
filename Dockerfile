FROM python:3.9
RUN apt-get update && \
    apt-get -y install nginx redis-server ssl-cert tzdata && \
    rm -rf /var/lib/apt/lists/* 

RUN mkdir -p /app/trunkplayer
WORKDIR /app/trunkplayer

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# install dependencies
ADD requirements.txt /app/trunkplayer
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /var/log/trunk-player/

# Make SSL
RUN make-ssl-cert generate-default-snakeoil --force-overwrite 

# copy project
#COPY . .
ADD . /app/trunkplayer
RUN rm -f /etc/nginx/sites-enabled/default
COPY trunk_player/trunk_player.nginx.docker /etc/nginx/conf.d/nginx.conf

EXPOSE 80
EXPOSE 443

ENTRYPOINT ["./entrypoint.sh"]

