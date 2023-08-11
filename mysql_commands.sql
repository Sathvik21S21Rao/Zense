create database ai_chat;
use ai_chat;
create table Users
(
    id varchar(100) primary key,
    password varchar(150) not null,
    email varchar(30) not null unique
);