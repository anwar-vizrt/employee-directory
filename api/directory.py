import aiopg
import bcrypt
import datetime
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.locks
import tornado.options
import tornado.web
import base64

from tornado.options import define, options

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


class ViewHandler(BaseHandler):
    async def get(self, userid):
        if userid:
            try:
                auth_header = self.request.headers.get('Authorization')
                if auth_header is None or not auth_header.startswith('Basic'):
                    self.send_not_authorized()
                    return False
                else:
                    auth_decoded = base64.b64decode(bytes(auth_header[6:], 'utf-8'))
                    username, password = auth_decoded.decode('utf-8').split(':', 2)
                    entry = await self.getuserbyid(userid)
                    if username is None or username != str(entry['username']) or password is None or password != entry['hashed_password']:
                        self.send_not_authorized()

                    birthdate_ = entry['birthdate']
                    if isinstance(birthdate_, datetime.date):
                        birthdate_ = birthdate_.strftime('%d-%m-%Y')
                    response = {'id': entry['id'],
                                'username': entry['username'],
                                'firstname': entry['firstname'],
                                'lastname': entry['lastname'],
                                'email': entry['email'],
                                'phonenumber': entry['phonenumber'],
                                'password': entry['hashed_password'],
                                'birthdate': birthdate_}
                    self.write(response)
            except NoResultError:
                raise tornado.web.HTTPError(404)
        else:
            raise tornado.web.HTTPError(400)


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class AddEmployeeHandler(BaseHandler):
    async def post(self):
        json_data = tornado.escape.json_decode(self.request.body)
        print(json_data['username'])
        user = await self.getuserbyname(json_data['username'])
        if user is not None and user['username'] == json_data['username']:
            raise tornado.web.HTTPError(400, "employee already exists")
        else:
            hash_password = tornado.ioloop.IOLoop.current().run_in_executor(
                None, bcrypt.hashpw, tornado.escape.utf8(json_data['password']),
                bcrypt.gensalt()
            )
            userid = await self.queryone(
            "INSERT INTO employees ( email ,username ,firstname ,lastname ,birthdate ,hashed_password,phonenumber)"
            "VALUES (%s,%s,%s,%s,  to_date(%s, 'DD-MM-YYY'), %s, %s) RETURNING id",
            json_data['email'], json_data['username'], json_data['firstname'], json_data['lastname'], json_data['birthdate'], hash_password, json_data['phonenumber']
        )
        self.set_status(201)


class Application(tornado.web.Application):
    def __init__(self, db):
        self.db = db
        handlers = [
            (r"/employee", HomeHandler),
            (r"/employee/(\d+)", ViewHandler),
            (r"/employees", AddEmployeeHandler),
        ]
        settings = dict(
            blog_title=u"Hello world",
           # debug=True,
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

        # In this demo the server will simply run until interrupted
        # with Ctrl-C, but if you want to shut down more gracefully,
        # call shutdown_event.set().
        shutdown_event = tornado.locks.Event()
        await shutdown_event.wait()


if __name__ == "__main__":
    tornado.ioloop.IOLoop.current().run_sync(main)
