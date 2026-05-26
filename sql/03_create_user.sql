CREATE USER petshop_user WITH PASSWORD 'petshop_password';

GRANT CONNECT ON DATABASE postgres TO petshop_user;

GRANT USAGE ON SCHEMA public TO petshop_user;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO petshop_user;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO petshop_user;
