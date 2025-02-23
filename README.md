# SkillHub
> Un sistema de gestión y consulta de hard y soft skills, que permite poner en contacto y compartir experiencia profesional y habilidades entre miembros de una organización.

## Qué es y qué hace?
SkillHub permite a sus usuarios descubrir personas con habilidades y competencias afines para facilitar la distribución del conocimiento.
Los usuarios cuentan con la capacidad de crear habilidades, issues resueltos (problemas que han solucionado) y guías (explicaciones de la resolución de un problema), y por supuesto, consultar las del resto de usuarios.
Estás habilidades están asociadas y referenciadas mutuamente para crear una base de conocimiento útil, y permiten la búsqueda y filtro para encontrar a la persona con la experiencia adecuada para cualquier reto.

## Cómo lo hicimos
SkillHub utiliza una base de datos SQL, con un backend Fast API y un front que utiliza Alpine.js y Tailwind CSS.
Para el desarrollo colaborativo, despliegue y testeo, utilizamos contenedores de Docker y GitHub para el control de versiones.

## Inspiración
El proyecto surgió en el HackUDC 2025, inspirado por la sugerencia de Gradiant; nos interesó por las oportunidades de aprendizaje y la cantidad de caminos que sen podía tomar en el desarrollo.

## TODO
- [x] more examples and test data
- [x] issues and guide creation with natural language
- [ ] ranking users page
- [x] Frontend migration to alpine
- [x] search bar updated when searching
- [x] chatbot helper for complex querys
- [ ] Skill recommendations based on existing skills
- [x] login and logout system
- [x] base nav component
- [ ] añadir a que equipo pertenece cada user 
 
## Quick Start

1. El único requisito necesario es tener Docker instalado en el sistema.
2. Una vez instalado, ejecuta uno de los siguientes comandos (dependerá de tu sistema operativo):

```sh
docker compose down && docker compose up --build
```
```sh
docker-compose down && docker-compose up --build
```

Tras ejecutarlo, los servicios estarán disponibles en las siguientes direcciones:
- Frontend: http://localhost:8000
- API: http://localhost:8000
- Database: localhost:5432

Además, se usarán las siguientes variables de entorno:

### Database

- POSTGRES_USER: `admin`
- POSTGRES_PASSWORD: `password123`
- POSTGRES_DB: `skills_db`

### API

- DATABASE_URL: `postgresql://admin:password123@db:5432/skills_db`
- SECRET_KEY: `your-secret-key-here`

> [!CAUTION]
> Alerta sobre seguridad
> 
> Para un posible despliegue en producción;
>
> 1. Cambia las constraseñas por defecto
> 2. Gestiona adecuadamente tus secrets
> 3. Configura ajustes de CORS
> 4. Habilita SSL/TLS
> 5. Configura mecanismos de autenticación adecuados

## Estructura del Proyecto

## Estructura del Proyecto

```
.
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   └── style.css
│   ├── templates/
│   │   └── index.html
│   ├── Dockerfile
│   └── nginx.conf
├── database/
│   └── init/
├── docker-compose.yml
└── README.md
```

## Diagrama de la Base de Datos

<img src="database/model_diagram.png" width="550">
</img>

## Cómo contribuír?
Este es un proyecto Open Source / de código abierto!
Por ello, las contribuciones siempre son bienvenidas. Para contribuír, sigue los siguientes pasos:

    Paso 1: Haz un fork del proyecto. Antes de colaborar, debes crear tu propia copia del código.
    Paso 2: Clona el proyecto.
    Paso 3: Crea una nueva rama.
    Paso 4: Desarrolla, añade los cambios al stage, y haz un commit.
    Paso 5: Haz un push de los cambios.
    Paso 6: Crea una pull request en el proyecto, y espera a ver su aceptación.  

