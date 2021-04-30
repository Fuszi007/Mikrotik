#!/bin/bash
sudo xhost +"local:docker@"
sudo docker-compose up -d
