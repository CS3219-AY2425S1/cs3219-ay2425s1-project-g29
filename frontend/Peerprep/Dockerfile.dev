# ARG for Node version
ARG NODE_VERSION=20.17.0

# Base image
FROM node:${NODE_VERSION}-slim AS base

WORKDIR /src

COPY package.json package-lock.json ./

RUN npm install

COPY . .


EXPOSE 3000:3000

CMD ["npm", "run", "dev"]
