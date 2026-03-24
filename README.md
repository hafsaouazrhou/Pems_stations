# Stopper l'ancien conteneur si nécessaire
docker stop pemsd7 && docker rm pemsd7

# Build
docker build -t pemsd7-app .

# Run
docker run -d -p 5000:5000 -p 27018:27017 --name pemsd7 pemsd7-app

