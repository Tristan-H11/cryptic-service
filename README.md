cryptic-service
============

The official service microservice of Cryptic (https://cryptic-game.net/).

## Testing with Docker

If you want to test this microservice you can simply build and run a 
container with docker-compose:

`docker-compose up -d`


## Testing with pipenv

You can also test it without docker using pipenv:

`pipenv run dev` or `pipenv run prod`

To install the dependencies manually use:

`pipenv install`

If you only need a mysql-server you can bring it up with:

`docker-compose up -d db`

## Docker-Hub

This microservice is online on docker-hub (https://hub.docker.com/r/useto/cryptic-service/).

## API Documentation



|Endpoint       | Data              | Functionality |
|---------      | ----------        |-------------- |
|create         |                   | create new service
|public_info    |                   | public info about an given service
|private_info   |                   | private info about an given service
|turn           |                   | turns service on/off
|delete         |                   | deletes service
|list           |                   | lists services on device
|part_owner     |                   | checks if you temporary part owner of this service
|hack           |                   | Bruteforce SSH