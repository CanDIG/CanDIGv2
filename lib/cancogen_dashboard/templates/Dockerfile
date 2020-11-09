FROM node:13.12.0-alpine

LABEL Maintainer="CanDIG Project"

COPY cancogen_dashboard /app/cancogen_dashboard

WORKDIR /app/cancogen_dashboard

ENV PATH /cancogen_dashboard/node_modules/.bin:$PATH

COPY package.json ./
COPY package-lock.json ./
RUN npm install


ENTRYPOINT ["npm", "start"]