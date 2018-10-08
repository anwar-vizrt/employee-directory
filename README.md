# Employee directory

This project is a prototype to build a rest api for employee directory in a secure way.

## Clone
This project can be cloned by running
```
git clone git@github.com:anwar-vizrt/employee-directory.git
```

## Run on docker container

This project can be run on docker containers easily. Here are the steps

1. Install latest version of [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) on your machine.
2. Now we need to build the project. To do that, change the directory to your project root directory and run
```
docker-compose build
```
3. Now we can start the containers by running

```
docker-compose up
```
4. Now we need to load the db with correct schema and seed the system with a user. We can do this by
```
docker container exec -i $(docker-compose ps -q db) psql directory admin < database/schema.sql
docker container exec -i $(docker-compose ps -q db) psql directory admin < database/constants.sql
```
Done! The application should be ready to use.
Note:
> If the `api` servers throws error while connecting to `db`. May be its a good time to restart the containers
```
docker-compose restart
```

## Using the api

The system is loaded with one manager user, there are only two types of user that can be created using
the api  `manager|regular`. A new user/employee can only be created by a manager. A regular user can
only see his/her personal information. He/She can also update their personal information. A manager is
allowed to create a new user, search a specific user with `username` or search all user.

### View employee

A employee information can be access via following url pattern

`http://<host>:<port>/employee/{id}`

If we are running the api locally in docker container as described above. We can access the default manager
info by doing a simple curl get request like below
```
curl -v -u admin:admin  http://localhost:8888/employee/1

```

### Update employee information
If we want to update this default manager personal information, we cam do this by http put request on the same url which is
unique for this user. To update the employee information we have to get/generate the current user json data
then update the fields that we are interested in then do a `PUT` request with the data to the same url.

Here is an example of updating the default manager info. Here we are changing the firstname to `Global`. Lets save this in a file called `data.json`
```
{
  "username": "admin",
  "passward": "$2b$12$hg34JSZJGZxYHPORdmDxRO0YGHA.B25wSJbD3RYHQodm2ZWvpBJj2",
  "firstname": "Global",
  "lastname": "Manager",
  "type": "manager",
  "birthdate": "08-07-1987",
  "email": "manager@exmaple.com",
  "phonenumber": "0123454"
}
```
Now lets do that update by

```
 curl -v -u admin:admin  -X PUT http://localhost:8888/employee/1 --upload-file /tmp/data.json
```
### Create new employee

A manager can create a new employee only. It can be done by posting a json data in to following url
```
http://<host>:<port>/employees
```

For the local environment. Here is an example. Save the following json data in a file called `data.json`
```
{
  "username": "another",
  "password": "another",
  "firstname": "foofoo",
  "lastname": "blabla",
  "email": "another@example.com",
  "phonenumber": "013930303",
  "type": "regular",
  "birthdate": "08-07-1988"
}
```

Now do a `POST` request to the employee collection url like below

```
curl -u admin:admin http://localhost:8888/employees --upload-file data.json
```

### Search employee

A admin user can only search employees, it can be done by doing a get request url
```
curl -v -u admin:admin  http://localhost:8888/employee/search/
```
this will show all the employee in the system
Now if the manager want to search an specific employee he can do that by the username

```
 curl -v -u admin:admin  http://localhost:8888/employee/search/?name=admin
```

Important thing is here all the information like password, birthdate, firstname, lastname will be decrypted in this list for the user.
So the manager can only see email address and username, while searching for users.

## Limitations
There are certain limitation of this implementation
* The Manager will not be able to update any user information.
* The encryption is done based on a key provided by employee. If it is lost then he can not login anymore
* This uses basic Authentication may be using JWT or token based approach is more robust.
* No ssl termination on top of API for now for secure communication.