#!/bin/bash

show_help() {
  echo "Usage: up.sh [OPTION]"
  echo "Options:"
  echo "  build         Use --build option"
  echo "  -h, --help    Show this help message"
}

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  show_help
  exit 0
fi

COMPOSE_FILE="docker-compose.yml"
if [ "$1" == "build" ]; then
  docker compose -p app -f $COMPOSE_FILE --env-file ../.env up --build -d
else
  docker compose -p app -f $COMPOSE_FILE --env-file ../.env up -d
fi
