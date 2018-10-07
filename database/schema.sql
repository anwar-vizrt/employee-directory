-- To create the database:
--   CREATE DATABASE blog;
--   CREATE USER blog WITH PASSWORD 'blog';
--   GRANT ALL ON DATABASE blog TO blog;
--
-- To reload the tables:
--   psql -U blog -d blog < schema.sql

DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    email VARCHAR(1024) NOT NULL UNIQUE,
    username VARCHAR(20) NOT NULL UNIQUE,
    firstname VARCHAR (1024) NOT NULL,
    lastname VARCHAR(1024) NOT NULL,
    birthdate VARCHAR(1024) NOT NULL,
    hashed_password VARCHAR(1024) NOT NULL,
    type INT NOT NULL,
    phonenumber VARCHAR(1024) NOT NUll UNIQUE
);


DROP TABLE IF EXISTS permissions;
CREATE TABLE permissions (
      id SERIAL PRIMARY KEY,
      role_id INT NOT NULL,
      privilage_id INT NOT NULL
);

DROP TABLE IF EXISTS privilage;
CREATE TABLE privilage(
       id SERIAL PRIMARY KEY,
       actiontype VARCHAR(100) NOT NULL UNIQUE
);

DROP TABLE IF EXISTS employeeroles;
CREATE TABLE employeeroles(
       id SERIAL PRIMARY KEY,
       employee_id INT NOT NULL,
       role_id INT NOT NULL
);


