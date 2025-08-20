# Dockerfile
FROM node:18-alpine

WORKDIR /app

# create app (only first time)
RUN npx create-react-app . --template typescript

# copy package files
COPY package*.json ./

# install dependencies
RUN npm install

# copy all source code
COPY . .

# expose port
EXPOSE 3000

# start app
CMD ["npm", "start"]