# nrp
NRP, a unimaginative play on the name ERP, for the author to manage certain facerts of their life.

It is also an opportunity for the author to learn flask. There are several variations of a joke that is roughly many programmers will spend several hours of trial and error programming to save 15 minutes of [reading documentation](https://flask.palletsprojects.com/en/2.2.x/).

"Minimum viable product" covers all manner of sins and this project will be no exception.

The last gratuitious caveat is that this project is what happens when a infrastructure person tries to write their first fullstack project while sitting on the sofa with their spouse with the television on.

## Initial Features
- Record health metrics: mass(weight) and blood pressure to start.
- Record "daily habits".
- Daily Calorie Counting

## Database Setup
For development I'm using the [official Postgres Docker image.](https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/)

This will give you a postgres database listening on port 5432 and then login with the commandline client:
```
docker pull postgres
docker run -p 5432:5432 --name nrp-pgsql -e POSTGRES_PASSWORD=changeme -d postgres
psql -h localhost -U postgres
```

You can then create the required database and tables:
```
CREATE DATABASE nrp;
CREATE TABLE users ( uid SERIAL PRIMARY KEY, name TEXT, birthdate DATE, height SMALLINT, sex SMALLINT );
CREATE TABLE health_metrics ( uid INT, date DATE, mass REAL, systolic SMALLINT, diastolic SMALLINT );
CREATE TABLE habits ( date DATE, uid INTEGER, exercise BOOLEAN, stretch BOOLEAN, sit BOOLEAN, sss BOOLEAN, journal BOOLEAN, vitamins BOOLEAN, brush_am BOOLEAN, brush_pm BOOLEAN, floss BOOLEAN, water REAL, UNIQUE ( date, uid ));
CREATE TABLE food ( fid SERIAL PRIMARY KEY, description TEXT, precision REAL, calories REAL );
CREATE TABLE eaten_daily ( date DATE, uid INTEGER, fid INTEGER, quantity REAL );
```

Before the development is finished you'll need to insert some valid data.

## Helpful Links
- [USDA Food Database](https://fdc.nal.usda.gov/)
