#!/usr/env bash

docker-compose down
git checkout -- nginx/conf.d/services.conf
sed -ri "s:server_name localhost:server_name brapi.biodata.pt:g" nginx/conf.d/services.conf


docker-compose up --build -d
docker-compose exec gatekeeper apt update
docker-compose exec gatekeeper apt install python3-certbot-nginx -y
docker-compose exec gatekeeper certbot --agree-tos --eff-email -m brunovasquescosta@gmail.com -d brapi.biodata.pt


--------------

docker stash nginx/conf.d/services.conf
docker-compose up gatekeeper -d
docker stash pop
