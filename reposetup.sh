#!/usr/bin/env bash
set -e 

echo -n DOMAIN:
read DOMAIN

cd
mkdir git
cd git
git clone https://github.com/forestbiotech-lab/PHENO.git
cd PHENO
git submodule init
git submodule set-url ontobrapi-web  https://github.com/forestbiotech-lab/ontobrapi-web.git
git submodule set-url ontobrapi-admin  https://github.com/forestbiotech-lab/ontobrapi-admin.git
git submodule set-url ontobrapi-brapi  https://github.com/forestbiotech-lab/ontobrapi-brapi.git
git submodule update
cd ontobrapi-web
git checkout master
git pull origin master
cd ../ontobrapi-admin
git checkout main
git pull origin main
cd ../ontobrapi-brapi
git checkout master
git pull origin master
cd ..
git submodule sync

sed -ri "s:3001\:80:80\:80\"\n      - \"443\:443:g" docker-compose.yml
sed -r "s:server_name localhost:server_name brapi.biodata.pt:g" nginx/conf.d/services.conf

docker-compose up -d
docker-compose exec gatekeeper apt update
docker-compose exec gatekeeper apt install python3-certbot-nginx -y
docker-compose exec gatekeeper certbot --agree-tos --eff-email -m brunovasquescosta@gmail.com -d ${DOMAIN}


exit 0
