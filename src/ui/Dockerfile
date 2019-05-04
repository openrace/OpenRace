FROM node:11.6.0 as node

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# IMPORTANT: naming 'as base' is used by cross-platform image publication
FROM nginx:1.15.12-alpine as base

COPY --from=node /usr/src/app/dist/angular-ui /usr/share/nginx/html

COPY nginx.conf.template /etc/nginx/conf.d/nginx.conf.template

CMD envsubst '$$MQTT_WEBSOCKETS_HOST' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'
