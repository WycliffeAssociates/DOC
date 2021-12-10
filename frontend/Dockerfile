# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:17.2.0-bullseye-slim as build-stage

RUN apt-get update && apt-get install -y \
    python3  \
    make  \
    g++

WORKDIR /app

COPY *.json /app/

RUN npm install
# FIXME Choose the correct commit hash or tag
# RUN npm install linearcombination/InterleavedResourcesGeneratorUI#a8930

COPY ./ /app/

# ARG FRONTEND_ENV=production

# Comment out the next line to disable tests
# RUN npm run test:unit

RUN npm run build
RUN npm start


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.21.4

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY --from=build-stage /nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
