# Stage 1: Build the React app
FROM docker.io/library/node:22-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# Stage 2: Serve with Nginx
FROM docker.io/library/nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# nginx master process needs root to manage worker processes.
# Worker processes run as the unprivileged 'nginx' user (nginx default).
# Inside a rootless Podman container, root is already unprivileged on the host.

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
