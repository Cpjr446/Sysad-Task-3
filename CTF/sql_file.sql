CREATE DATABASE sql_injection_demo;
USE sql_injection_demo;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50),
    flag VARCHAR(255)
);

INSERT INTO users (username, password, flag) VALUES ('admin', 'password', 'FLAG{hidden_flag}');
