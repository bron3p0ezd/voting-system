FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --timing --verbose --no-audit --no-fund

COPY . .

ARG VITE_API_BASE_URL=/api/v1

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build && cp -a dist /frontend-dist
