# Base Ubuntu Dockerfile
FROM ubuntu:latest
MAINTAINER biodepot

RUN apt-get update
RUN apt-get install -y python3 python3-pip wget


WORKDIR /home