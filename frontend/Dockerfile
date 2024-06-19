# Stage 0: build the frontend.
FROM node:22-bookworm-slim as build-stage

RUN apt-get update && apt-get install -y \
    python3  \
    make  \
    g++

WORKDIR /app

ARG PUBLIC_DOC_VERSION_ARG
ARG PUBLIC_DOC_BUILD_TIMESTAMP_ARG
ENV PUBLIC_DOC_VERSION ${PUBLIC_DOC_VERSION_ARG}
ENV PUBLIC_DOC_BUILD_TIMESTAMP ${PUBLIC_DOC_BUILD_TIMESTAMP_ARG}

COPY package*.json .
RUN npm ci
COPY . .
RUN npm run check
RUN npm run build

# Stage 1: Let nginx serve the built front-end in production.
FROM nginx:1.27

COPY --from=build-stage /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
COPY --from=build-stage /app/build/ /usr/share/nginx/html
COPY --from=build-stage /app/package.json .

EXPOSE 80

CMD ["/bin/sh",  "-c",  "exec nginx -g 'daemon off;'"]
