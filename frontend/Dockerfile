# Estágio 1

FROM node:18-alpine AS builder

WORKDIR /app


COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile

COPY . .


# Executa o build de produção
RUN yarn build

# Estágio 2:
FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 