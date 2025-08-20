FROM node:18-alpine
WORKDIR /app
RUN npx create-react-app my-app
WORKDIR /app/my-app
RUN npm run build
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "-s", "build", "-p", "3000", "-H", "0.0.0.0"]