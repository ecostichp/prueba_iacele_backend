# Aplicación prueba FullStack IACele


## Descripción de la aplicación

La aplicación es de prueba, pero es funcional. No tiene nada de "lógica de negocios" todía. Sin embargo la lógica de programación está casí completa.



El código es público:
 -El código del backend está en [GitHub](https://github.com/ecostichp/inventario_app_backend)
 -El código del frontend está en [GitHub](https://github.com/ecostichp/prueba_iacele_frontend)



La estructura de la aplicación queda de la siguiente manera:

1.- Backend FastAPI
  1.1.- Hosting: Google Cloud Run (con Docker)
  1.2.- ORM: SQLAlchemy

2A.- Database Motor para Producción: PostgreSQL
  2A.1.- Hosting: Google Cloud SQL

2B.- Database Motor para Testing: SQLite
  2B.1.- Hosting: Local


3.- Frontend ReactJS
  3.1.- Hosting: Vercel
  3.2.- Ruteador: React-Router-Dom
  3.3.- Peticiones HTTP: Axios
  3.4.- CSS: TailwindCSS
  3.4.- UI components: TailwindUI





## El Backend

Este repositorio sólo abarca la parte del backend


### 1. Actualiza PIP en python.
```
python -m pip install -U Pip  
```

### 2. Crea un entorno para el proyecto.
En este ejemplo, el entorno se llamará "env-iaCeleApp"

```
python -m venv env-iaCeleApp
```

### 3. Activa el entorno.
```
env-iaCeleApp\Scripts\activate
```

### 4. Actualiza PIP en tu entorno e instala las dependencias del proyecto.
```
python -m pip install -U Pip  
python -m pip install -r requirements.txt
```

### 5. Inicia el servidor.

Sitúate dentro de la carpeta del backend: PRUEBA_IACELE_BACKEND/

```
uvicorn app.main:app --reload
```
Si quieres iniciar el servidor en otro host (ej: 192.168.1.82):
```
uvicorn app.main:app --reload  --host 192.168.1.82
```





# El Motor de Base de Datos.
El proyecto sólo usa 2 motores de bases de datos:

Para producción y desarrollo se va a utilizar PostgreSQL. La database se aloja en los servidores de GCloud.

Para testing se va a utilizar SQLite. La database se aloja de manera Local y puedes configurar nombre y dirección de la misma dentro del archivo 'app/database/orm.py'.



En el archivo 'app/database/orm.py' hay 3 configuraciones al 'engine' del ORM para correr la aplicación:

  1.- Modo Producción: 
    a) Backend de manera remota, alojado en GCloud Run.
    b) Database de manera remota (PostgreSQL), alojado en GCloud SQL. 
    c) La comunicación entre ellos hace de manera local (Configuración especial que se hace posible al tener ambos servidores en la misma nube).
  
  2.- Modo Desarrollo:
    a) Backend de manera local.
    b) Database de manera remota (PostgreSQL), alojado en GCloud SQL.
    c) La comunicación entre ellos hace de manera remota.

  3.- Modo Testing:
    a) Backend de manera local.
    b) Database de manera local (SQLite).
    c) La comunicación entre ellos hace de manera local.