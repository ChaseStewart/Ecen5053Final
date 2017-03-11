
-- first create DB
DROP DATABASE IF EXISTS users_data;
CREATE DATABASE users_data;
USE users_data;

-- now create all tables
CREATE TABLE users_data (name VARCHAR(20),email VARCHAR(20),password VARCHAR(20),access VARCHAR(20));

-- then create the user
CREATE USER 'rpi'@'128.138.%' IDENTIFIED BY 'mounika';
GRANT ALL ON users_data.* to 'rpi'@'128.138.%';


