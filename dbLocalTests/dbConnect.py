gcloud_sql_host = "34.94.9.168"
gcloud_sql_db = 'iaceledb'
gcloud_sql_user = "licCostich"
gcloud_sql_password = "Lic@123456"


dbConfigLocal = {
    'host': gcloud_sql_host,
    'database': gcloud_sql_db,
    'user': gcloud_sql_user,
    'password': gcloud_sql_password
}


# GRANT SELECT, INSERT, UPDATE, DELETE ON usuarios, clientes, productos, proveedores TO iacele_app;
# GRANT USAGE, SELECT ON SEQUENCE sequence_name TO user_role_name;

# SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name='mytable';
# select * from information_schema.sequences;

# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA schema_name TO your_user;
# GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA schema_name TO your_user;
# GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA schema_name TO your_user;

# SELECT current_schema();
