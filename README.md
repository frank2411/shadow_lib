# shadow_lib

Techincal test for shadow

# How to run the project

```shell

# First start the docker compose services
docker compose up -d

# Once the services started apply db migrations
docker compose exec web alembic upgrade head

# Populate the databse with a superadmin user, a customer, an author, a book and an order for the created book. HAVE FUN NOW!
docker compose exec web flask populate-db

```
### Default created user will have
### email = test@test.com and password = admin

```shell
# OPTIONAL - Create a superadmin user (it's not very useful for the sake of this test but, still)
docker compose exec web flask create-superadmin --email=<choose_email> --pasword=<choose_password>
# Output should be something like -> Created superadmin user with email <chosen_email>
```

## Explore the API

In order to play with the API a full documented swagger is available. You just need to go to: http://localhost:5000/api/v1/docs !

A simple book search endpoint is also provided (and documented).


# Bonus steps

### Create a superadmin token that doesn't expire (for the sake of testing).

```shell
# Run
docker compose exec web flask create-superadmin-token --email=<choose_email> --pasword=<choose_password>
```

Output should be something like:

```shell
Access token id: 53871016-1df1-49e9-972e-91fcfbcfcf41

Refresh token id: bf48da01-1876-40b8-a44d-a32d0d800740

Access token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzQ0ODMwMjgsIm5iZiI6MTY3NDQ4MzAyOCwianRpIjoiNTM4NzEwMTYtMWRmMS00OWU5LTk3MmUtOTFmY2ZiY2ZjZjQxIiwidHlwZSI6ImFjY2VzcyIsImlzcyI6InNoYWRvd19saWIiLCJleHAiOjE3Mzc1NTUwMjgsInVzZXJfaWQiOiIyODNmMzNmYS0zYmYxLTRlNzktOGFhOC0xOTMzNGU3ZTk4YzkiLCJlbWFpbCI6ImZyYW5jZXNjby5wZXJuYUBnbWFpbC5jb20iLCJyb2xlIjoic3VwZXJhZG1pbiJ9.ithdGyVJIRV8bZ8jJmxl79aXcemYkb6ACX8kVJdSEBk

Refresh token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzQ0ODMwMjgsIm5iZiI6MTY3NDQ4MzAyOCwianRpIjoiYmY0OGRhMDEtMTg3Ni00MGI4LWE0NGQtYTMyZDBkODAwNzQwIiwidHlwZSI6InJlZnJlc2giLCJpc3MiOiJzaGFkb3dfbGliIiwiZXhwIjoxNzY5MDkxMDI4LCJ1c2VyX2lkIjoiMjgzZjMzZmEtM2JmMS00ZTc5LThhYTgtMTkzMzRlN2U5OGM5IiwiZW1haWwiOiJmcmFuY2VzY28ucGVybmFAZ21haWwuY29tIiwicm9sZSI6InN1cGVyYWRtaW4ifQ.H1D7Au9xPPsbvGZHe6vj9SFoOA1gYxC6HzPTmXolo-c

```

# Specs

In the `analysis` folder you should find the DB schema and a simple diagram flow


# Run the tests locally
To run the tests you have to (a database is required, you could use the one in the docker compose):

```shell
 # pip insatall dependencies
 pip install -e ".[dev]"
 
 # create test_db
 postgres=# create database test_db;
 
 # run tox
 tox
```









