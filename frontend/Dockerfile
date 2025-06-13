FROM node:18-alpine

WORKDIR /app

# Dependencies installieren
COPY package*.json ./
RUN npm install

# App-Code kopieren
COPY . .

EXPOSE 3000

# Development-Server starten
CMD ["npm", "start"] 