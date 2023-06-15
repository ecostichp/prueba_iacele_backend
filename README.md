# Ejercicio 01 de FullStacK

Para generar esta aplicación FullStack me basé casi en su totalidad a la aplicación de Sixfwa en el canal de Youtube Rithmic. El video de [YouTube](https://youtu.be/UbSONbZ8t4g) y el código [GitHub](https://github.com/sixfwa/react-fastapi) son públicos.


Mi aplicación queda de la siguiente manera:
1.- Backend FastAPI
2.- Frontend ReactJS
3.- Database Motor SQLite
4.- ORM SQLAlchemy.

A diferencia de Rithmic, yo cree el proyecto con VITE. Además incluí "Axios" para las peticiones al backend y para el CSS incluí "TailwindCSS".



# El Backend


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
python -m pip install -U FastAPI[all] PassLib[bcrypt] PyJWT SQLAlchemy
```

### 5. Inicia el servidor.
```
uvicorn app.main:app --reload
```
Si quieres iniciar el servidor en otro host (ej: 192.168.1.82):
```
uvicorn app.main:app --reload  --host 192.168.1.82
```
