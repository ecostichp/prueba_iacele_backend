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

2.- Database Motor SQLite
  2.1.- Hosting: dentro del contenedor Docker del backend


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
En este ejemplo, el entorno se llamará "env"

```
python -m venv env
```

### 3. Activa el entorno.
```
env\Scripts\activate
```

### 4. Actualiza PIP en tu entorno e instala las dependencias del proyecto.
```
python -m pip install -U Pip  
python -m pip install -r requirements.txt
```

### 5. Inicia el servidor.

Sitúate dentro de la carpeta app/

```
uvicorn main:app --reload
```
Si quieres iniciar el servidor en otro host (ej: 192.168.1.82):
```
uvicorn main:app --reload  --host 192.168.1.82
```





# El Motor de Base de Datos.
Se va a utilizar SQLite como el motor de la base de datos. Puedes configurar nombre y dirección de esta base de datos dentro del archivo 'app/database/orm.py'.