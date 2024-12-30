# print current working directory 
pwd # make sure you are on assignment-3-chick-fil-a/a3
# cd ./src/a3

# Redis container (lsh-redis-data): 
# Python Application container (my-redis-app): contains code to read data from a TSV file and store it in Redis.
# Docker network (chickfila-lsh):  

# Pull Redis image (if not already done)
docker pull redis

# Rebuild the docker image
pwd
# docker build --no-cache -t my-redis-app .
docker build --no-cache -t my-redis-app . #./src/a3

# Stop and Remove the Running Container:
docker stop lsh-redis-data my-redis-app
docker rm lsh-redis-data my-redis-app

# remove and rebuild network 
docker network rm chickfila-lsh
docker network create chickfila-lsh

# start redis container
docker run --name lsh-redis-data --network chickfila-lsh -d redis

# run application container 
# - run to execute python 
# docker run --name my-redis-app --network chickfila-lsh -v "$(pwd):/app" my-redis-app
docker run --name my-redis-app --network chickfila-lsh -p 5001:5001 -v "$(pwd):/app" my-redis-app

# # stop and remove containers
# docker-compose down

# # using docker-compose up --build for simplicity 
# docker-compose up --build 

# Enable retrieve information by key from redis cli
docker exec -it lsh-redis-data redis-cli


