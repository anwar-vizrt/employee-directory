import aiopg
import base64
import bcrypt
import json
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.locks
import tornado.options
import tornado.web
from domains.domain import Employee
from tornado.options import define, options
from util.constants import Roles

define("port", default=8888, help="run on the given port", type=int)
define("db_host", default="127.0.0.1", help="blog database host")
define("db_port", default=5432, help="blog database port")
define("db_database", default="symatec", help="blog database name")
define("db_user", default="directory", help="blog database user")
define("db_password", default="directory", help="blog database password")


class NoResultError(Exception):
    pass


class BaseHandler(tornado.web.RequestHandler):
    def row_to_obj(self, row, cur):
        """Convert a SQL row to an object supporting dict and attribute access."""
        obj = tornado.util.ObjectDict()
        for val, desc in zip(row, cur.description):
            obj[desc.name] = val
        return obj

    async def execute(self, stmt, *args):
        """Execute a SQL statement.

        Must be called with ``await self.execute(...)``
        """
        with (await self.application.db.cursor()) as cur:
            await cur.execute(stmt, args)

    async def query(self, stmt, *args):
        """Query for a list of results.

        Typical usage::

            results = await self.query(...)

        Or::

            for row in await self.query(...)
        """
        with (await self.application.db.cursor()) as cur:
            await cur.execute(stmt, args)
            return [self.row_to_obj(row, cur)
                    for row in await cur.fetchall()]

    async def queryone(self, stmt, *args):
        """Query for exactly one result.

        Raises NoResultError if there are no results, or ValueError if
        there are more than one.
        """
        results = await self.query(stmt, *args)
        if len(results) == 0:
            raise NoResultError()
        elif len(results) > 1:
            raise ValueError("Expected 1 result, got %d" % len(results))
        return results[0]

    async def getuserbyid(self, user_id):

        if user_id:
            return await self.queryone("SELECT * FROM employees WHERE id = %s", int(user_id))

    async def getuserbyname(self, username):

        if username:
            return await self.queryone("SELECT * FROM employees WHERE username = %s", username)

    async def employee_exists(self, user_id):
        return bool(await self.queryone("SELECT * FROM employees where id = %s", int(user_id)))

    def send_not_authorized(self):
        raise tornado.web.HTTPError(401)

    def send_forbidden(self):
        raise tornado.web.HTTPError(403)


class AuthenticationHandler(BaseHandler):
    """
    Checks user authentication credentials and returns boolean result.
    True means authorized user
    False means unauthorized user
    """

    async def isAuthorized(self, user):
        try:
            auth_header = self.request.headers.get('Authorization')
            if auth_header is None or not auth_header.startswith('Basic'):
                return False
            else:
                auth_decoded = base64.b64decode(bytes(auth_header[6:], 'utf-8'))
                username, password = auth_decoded.decode('utf-8').split(':', 2)
                hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
                    None, bcrypt.hashpw, tornado.escape.utf8(password),
                    tornado.escape.utf8(user.hashed_password))
                hashed_password = tornado.escape.to_unicode(hashed_password)
                if username is None or username != user.username or hashed_password is None or hashed_password != user.hashed_password:
                    return False
                else:
                    return True
        except NoResultError:
            return False

    def getUsernameFromAuthHeader(self):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic'):
            return None
        else:
            auth_decoded = base64.b64decode(bytes(auth_header[6:], 'utf-8'))
            username, password = auth_decoded.decode('utf-8').split(':', 2)
            return username

    def getPasswordFromAuthHeader(self):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic'):
            return None
        else:
            auth_decoded = base64.b64decode(bytes(auth_header[6:], 'utf-8'))
            username, password = auth_decoded.decode('utf-8').split(':', 2)
            return password

    async def userExists(self, username):
        if username:
            try:
                user = await self.getuserbyname(username)
                return True
            except NoResultError:
                return False

    async def generate_hashed_password(self, password):
        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None, bcrypt.hashpw, tornado.escape.utf8(password),
            bcrypt.gensalt()
        )
        return tornado.escape.to_unicode(hashed_password)

    async def get_hashed_password(self, newpassword, hashed_password):
        new_hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None, bcrypt.hashpw, tornado.escape.utf8(newpassword),
            tornado.escape.utf8(hashed_password))
        return tornado.escape.to_unicode(new_hashed_password)


class EmployeeHandler(AuthenticationHandler):
    async def get(self, userid):
        if userid:
            try:
                user = await self.getuserbyid(userid)
                authorized = await self.isAuthorized(user)
                if authorized is not True:
                    self.send_not_authorized()
                else:
                    employee = Employee(None, user)
                    employee.decrypt(self.getPasswordFromAuthHeader())
                    self.write(employee.toJson())
            except NoResultError:
                raise tornado.web.HTTPError(404)
        else:
            raise tornado.web.HTTPError(400)

    async def put(self, userid):
        if userid:
            try:
                user = await self.getuserbyid(userid)
                authorized = await self.isAuthorized(user)
                if authorized is not True:
                    self.send_not_authorized()
                else:
                    print(self.request.body)
                    json_data = tornado.escape.json_decode(self.request.body)
                    updated_employee = Employee(json_data)
                    updated_employee.encrypt(updated_employee.getPassword())
                    updated_employee.set_hashed_password(
                        await self.get_hashed_password(json_data['password'], user.hashed_password))
                    employee = Employee(None, user)
                    if employee.equals(updated_employee):
                        self.set_status(304)
                        return False
                    if json_data:

                        if employee.getUsername() != updated_employee.getUsername():
                            print("Not allowed to change the username ", user.username)
                            raise tornado.web.HTTPError(403)
                        else:
                            updateUser = await self.queryone(
                                "UPDATE employees SET ( email ,username ,firstname ,lastname ,birthdate ,hashed_password, type, phonenumber) = "
                                "(%s,%s,%s,%s, %s, %s, %s, %s) where id = %s RETURNING id",
                                updated_employee.getEmail(),
                                updated_employee.getUsername(),
                                updated_employee.getFirstname(),
                                updated_employee.getLastname(),
                                updated_employee.getBirthdate(),
                                updated_employee.getPassword(),
                                updated_employee.getType(),
                                updated_employee.getPhonenumber(),
                                userid
                            )
                            print("Updated user id : ", updateUser.id)
            except NoResultError:
                raise tornado.web.HTTPError(404)
        else:
            raise tornado.web.HTTPError(400)


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class AddEmployeeHandler(AuthenticationHandler):
    async def post(self):
        username = self.getUsernameFromAuthHeader()
        if username is None:
            self.send_not_authorized()
        else:
            user = await self.getuserbyname(username)
            authorized = await self.isAuthorized(user)
            authorized_employee = Employee(None, user)
            if authorized is False:
                self.send_not_authorized()
            json_data = tornado.escape.json_decode(self.request.body)
            employee_to_add = Employee(json_data)
            if authorized_employee.getType() != Roles.RoleType['manager']:
                self.send_forbidden()
            try:
                user = await self.getuserbyname(employee_to_add.getUsername())
            except NoResultError:
                print("No employee_to_add exists, so we can create now")
            if user is not None and user['username'] == employee_to_add.getUsername():
                raise tornado.web.HTTPError(400, "employee_to_add already exists")
            else:
                employee_to_add.encrypt(employee_to_add.getPassword())
                hashed_password = await self.generate_hashed_password(employee_to_add.getPassword())
                employee_to_add.set_hashed_password(hashed_password)
            newUser = await self.queryone(
                "INSERT INTO employees ( email ,username ,firstname ,lastname ,birthdate ,hashed_password, type, phonenumber)"
                "VALUES (%s,%s,%s,%s, %s, %s,%s,%s) RETURNING id",
                employee_to_add.getEmail(),
                employee_to_add.getUsername(),
                employee_to_add.getFirstname(),
                employee_to_add.getLastname(),
                employee_to_add.getBirthdate(),
                employee_to_add.getPassword(),
                employee_to_add.getType(),
                employee_to_add.getPhonenumber(),
            )
        self.set_header("Location", "http://localhost:8888/employee/{0}".format(newUser.id))
        self.set_status(201)


class SearchHandler(AuthenticationHandler):
    async def get(self, **param):
        username = self.getUsernameFromAuthHeader()
        if username is None:
            self.send_not_authorized()
        else:
            user = await self.getuserbyname(username)
            authorized = await self.isAuthorized(user)
            authorized_employee = Employee(None, user)
            if authorized is False:
                self.send_not_authorized()
            if authorized_employee.getType() != Roles.RoleType['manager']:
                self.send_forbidden()
            searchResult = None
            json_array = []
            queryParam = self.get_argument('name', None, True)
            if queryParam is not None:
                searchResult = await self.query("Select * from employees where username = %s", queryParam)
            else:
                searchResult = await self.query("Select * from employees")
            for result in searchResult:
                employee = Employee(None, result)
                json_array.append(employee.toJson())
            response = json.dumps(json_array)
            self.write(response)


class Application(tornado.web.Application):
    def __init__(self, db):
        self.db = db
        handlers = [
            (r"/employee", HomeHandler),
            (r"/employee/(\d+)", EmployeeHandler),
            (r"/employees", AddEmployeeHandler),
            (r"/employee/search", SearchHandler),
            (r"/employee/search/?(?P<name>[A-Za-z0-9-]+)?/", SearchHandler)
        ]
        settings = dict(
            blog_title=u"Hello world",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)


async def main():
    tornado.options.parse_command_line()

    # Create the global connection pool.
    async with aiopg.create_pool(
            host=options.db_host,
            port=options.db_port,
            user=options.db_user,
            password=options.db_password,
            dbname=options.db_database) as db:
        app = Application(db)
        app.listen(options.port)

        shutdown_event = tornado.locks.Event()
        await shutdown_event.wait()


if __name__ == "__main__":
    tornado.ioloop.IOLoop.current().run_sync(main)
