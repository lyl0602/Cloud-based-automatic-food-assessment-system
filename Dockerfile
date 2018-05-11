FROM ubuntu:latest


RUN apt-get update
RUN apt-get install default-jre
RUN apt-get install default-jdk



ADD webapp.jar /tmp


EXPOSE 80


CMD nohup java -jar webapp.jar &