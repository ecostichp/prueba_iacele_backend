from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gcloud_sql_host: str
    gcloud_sql_name: str
    gcloud_sql_db: str
    gcloud_sql_user: str
    gcloud_sql_password: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()


dbConfig = {
        'host' : settings.gcloud_sql_host,
        'database': settings.gcloud_sql_db,
        'user': settings.gcloud_sql_user,
        'password': settings.gcloud_sql_password
        }