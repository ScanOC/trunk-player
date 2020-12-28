FROM dreinhold/base-django:1.1


RUN mkdir -p /app/trunkplayer
# set work directory
WORKDIR /app/trunkplayer

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
#COPY . .
ADD . /app/trunkplayer
RUN rm -f /etc/nginx/sites-enabled/default
COPY trunk_player/trunk_player.nginx.docker /etc/nginx/conf.d/nginx.conf

# install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]

