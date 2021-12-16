# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:17.2.0-bullseye-slim as build-stage

RUN apt-get update && apt-get install -y \
    python3  \
    make  \
    g++

WORKDIR /app

COPY *.json /app/

RUN npm install

COPY ./ /app/

# Comment out the next line to disable tests
# RUN npm run test:unit

# npm run build will run snowpack build which will create the
# directory ./build/_dist_  containing the built project.
RUN npm run build

# Run the frontend
CMD ["npm", "start"]

# You can build this container thusly:
# docker build -t frontend .

# You can run the container thusly:
# docker run -d -it -p 8000:8000 frontend

# Finally you can access the UI (assuming bridge network to localhost)
# at http://localhost:8000

# Optional nginx front to frontend JS
# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
# FROM nginx:1.21.4

# COPY --from=build-stage /app/build/_dist_/ /usr/share/nginx/html

# COPY --from=build-stage /app/nginx.conf /etc/nginx/conf.d/default.conf
# COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
