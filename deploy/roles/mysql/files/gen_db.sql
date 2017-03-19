
-- first create DB
DROP DATABASE IF EXISTS users_data;
CREATE DATABASE users_data;
USE users_data;

-- now create all tables

-- create table with users data
CREATE TABLE users_data (name VARCHAR(20),email VARCHAR(20),password BINARY(64), access TINYINT(1) DEFAULT 0 );

-- create table for currently logged-in user
create table logged_in_users (timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, name varchar(20) NOT NULL );

-- create table with arm/disarm status
CREATE TABLE arm_status (timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, arm_state BOOL NOT NULL )

-- create reference access table for join queries
CREATE TABLE ref_access_table (id TINYINT(1), name VARCHAR(20));
insert into ref_access_table (id, name) VALUE (3, "Admin"); 
insert into ref_access_table (id, name) VALUE (2, "Reserved"); 
insert into ref_access_table (id, name) VALUE (1, "Child"); 
insert into ref_access_table (id, name) VALUE (0, "User"); 

-- create reference arm/disarm table for join queries
CREATE TABLE ref_arm_state    (id TINYINT(1), name VARCHAR(20));
insert into ref_arm_state (id, name) VALUE (0, "Armed");
insert into ref_arm_state (id, name) VALUE (1, "Disarmed");



-- then create the user
CREATE USER 'rpi'@'128.138.%' IDENTIFIED BY 'mounika';
GRANT ALL ON users_data.* to 'rpi'@'128.138.%';



-- finally, set trigger to put first user as admin
delimiter //

CREATE TRIGGER ADMIN_TEST 
BEFORE INSERT ON users_data
FOR EACH ROW 
BEGIN
DECLARE i INT;
	SET i = (select count(*) from users_data);
	if i = 0 THEN
		SET NEW.access = 3; 
	END IF; 
END;//

delimiter ;
