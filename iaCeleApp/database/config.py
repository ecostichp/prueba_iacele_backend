from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # sqlite: archivo local. postgres: IP pública desde tu máquina.
    # cloudsql: socket Unix. El contenedor fija este valor.
    db_mode: str = "sqlite"
    gcloud_sql_name: str
    gcloud_sql_ip: str
    gcloud_sql_db: str
    gcloud_sql_user: str
    gcloud_sql_password: str
    bucket_name: str
    odoo_clave_api: str
    odoo_db_api: str
    odoo_db_prueba_api: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
