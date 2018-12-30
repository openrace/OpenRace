FROM node:11.6.0 as node

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Stage 2
FROM nginx:1.15.8-alpine

COPY --from=node /usr/src/app/dist/angular-ui /usr/share/nginx/html

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
