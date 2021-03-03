FROM httpd:2.4
LABEL maintainer="BraveDragon"
LABEL version="1.0"
LABEL description="「AI-CardBattle」をDocker上に立ち上げたWebサーバー上で実行するためのDockerfile"

COPY ./CardBattle_WebGL/ /usr/local/apache2/htdocs/