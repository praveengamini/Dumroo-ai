# ---- 1. Build Stage ----
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies (ignore peer deps)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build production bundle
RUN npm run build


# ---- 2. Production Stage ----
FROM nginx:alpine

# Copy React build files to Nginx HTML folder
COPY --from=builder /app/dist /usr/share/nginx/html

# Remove default nginx config & replace with ours (optional but recommended)
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
