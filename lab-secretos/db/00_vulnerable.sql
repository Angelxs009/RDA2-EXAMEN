-- ESCENARIO INSEGURO (Fase 2): rol con privilegios administrativos innecesarios. Datos ficticios.
CREATE ROLE lab_vuln_admin LOGIN SUPERUSER PASSWORD 'admin123';
CREATE DATABASE lab_vuln OWNER lab_vuln_admin;
\connect lab_vuln
CREATE TABLE usuarios (id serial PRIMARY KEY, nombre text NOT NULL, email text NOT NULL, password_hash text NOT NULL);
CREATE TABLE productos (id serial PRIMARY KEY, nombre text NOT NULL, precio numeric(10,2) NOT NULL);
INSERT INTO usuarios (nombre,email,password_hash) VALUES
 ('Ana Torres','ana@example.com','$2b$10$FAKEHASHanaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'),
 ('Luis Mora','luis@example.com','$2b$10$FAKEHASHluisxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
INSERT INTO productos (nombre,precio) VALUES ('Cuaderno',2.50),('Lápiz',0.60),('Mochila',24.90);
ALTER TABLE usuarios OWNER TO lab_vuln_admin;
ALTER TABLE productos OWNER TO lab_vuln_admin;
