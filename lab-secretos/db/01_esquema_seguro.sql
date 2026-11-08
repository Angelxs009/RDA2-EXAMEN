-- ESCENARIO SEGURO (Fase 3): esquema + mínimo privilegio. Se ejecuta como el rol OWNER (DDL).
-- Variable psql :app = rol de runtime de la aplicación (creado por scripts/setup-db.js).
CREATE TABLE usuarios (
  id serial PRIMARY KEY, nombre text NOT NULL, email text NOT NULL, password_hash text NOT NULL);
CREATE TABLE productos (
  id serial PRIMARY KEY, nombre text NOT NULL, precio numeric(10,2) NOT NULL CHECK (precio >= 0));
INSERT INTO usuarios (nombre,email,password_hash) VALUES
 ('Ana Torres','ana@example.com','$2b$10$FAKEHASHanaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'),
 ('Luis Mora','luis@example.com','$2b$10$FAKEHASHluisxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
INSERT INTO productos (nombre,precio) VALUES ('Cuaderno',2.50),('Lápiz',0.60),('Mochila',24.90);

-- Mínimo privilegio para el rol de la aplicación
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO :"app";
GRANT SELECT, INSERT ON productos TO :"app";
GRANT USAGE ON SEQUENCE productos_id_seq TO :"app";
GRANT SELECT (id, nombre, email) ON usuarios TO :"app";   -- sin password_hash
