from flask import Flask
from flask_restful import Resource, Api, request
# from database import MySQLPool
# import functools
from functools import wraps


def start_transaction(*expected_args):
    def myDecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json_data = request.get_json()
            # print "here is json data: {}".format(json_data)
            # name will be inserted to db
            # name = json_data['name']
            # the xid number
            xid = json_data['xid']
            # add to db
            mysqlConnectionPool = expected_args[0]
            conn, cursor = mysqlConnectionPool.startQuery()
            cursor = mysqlConnectionPool.start_transaction(xid, cursor)
            if cursor is False:
                # adding to db failed
                print "Failed starting transaction"
                return func(*args, **kwargs)
            # adding to db with start transaction was successful
            # so this needs to be passed to function
            kwargs['query'] = cursor
            kwargs['db'] = mysqlConnectionPool
            # now in the function this is ran the varible query can do inserts
            # this runs function in route
            result = func(*args, **kwargs)
            cursor = result['query']
            db = result['db']
            # end the transaction
            db.end_transaction(str(xid), cursor)
            # stored query in logger under xid
            db.logger[str(xid)] = {"connection": conn,
                                   "cursor": cursor}
            return {'status':
                    "xid:{} started tx, insert, waiting on commit or roll".
                    format(xid)}
        return wrapper
    return myDecorator


def commit_or_rollback(*expected_args):
    def myDecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json_data = request.args
            xid = json_data['xid']
            action = json_data['action']
            # get the cursor  we are on
            mysqlConnectionPool = expected_args[0]
            cursor = mysqlConnectionPool.logger[str(xid)]['cursor']
            # commit or rollback
            response = None
            if action == 'rollback':
                # rollback
                response = mysqlConnectionPool.rollBack_transaction(
                    cursor, xid)
            else:
                # commit
                response = mysqlConnectionPool.commit_transaction(cursor, xid)
            if response is False:
                kwargs['error'] = action
            mysqlConnectionPool.closeConnection(
                mysqlConnectionPool.logger[str(xid)]['cursor'],
                mysqlConnectionPool.logger[str(xid)]['connection'])
            del mysqlConnectionPool.logger[str(xid)]
            results = func(*args, **kwargs)
            return results
        return wrapper
    return myDecorator


def create_app(db_connection):
    app = Flask(__name__)
    api = Api(app)
    app.config['DB'] = db_connection

    class transaction(Resource):
        # STARTING THE TRANSACTION
        @start_transaction(app.config['DB'])
        def post(self, query, db):
            # grab json vars
            x = request.get_json()
            name = x['name']
            # xid = x['xid']
            # insert name
            query = db.insert(query, name)
            if query is False:
                return {'status': "failed during insert"}
            # if to this point
            # have started transaction and still hold query
            # we will be sending back to decorator to hold in logger
            return {'query': query, 'db': db}

        # COMMIT OR ROLLBACK TRANSACTION
        @commit_or_rollback(app.config['DB'])
        def get(self, error=None):
            args = request.args
            xid = str(args['xid'])
            action = args['action']
            if error:
                return {'error': 'failed on {} of xid: {}'.format(error, xid)}
            return {'success': "xid: {} completed {}".format(xid, action)}

    class everythingInDB(Resource):
        # show everything in the db
        def get(self):
            x = app.config['DB']
            conn, cursor = x.startQuery()
            res = x.grabAll(cursor, conn)
            print res
            return res

    class everythingInLogger(Resource):
        def get(self):
            print "everything in the logger = "
            print app.config['DB'].logger
            amount = len(app.config['DB'].logger)
            return {'status': '{} items in the logger'.format(amount)}

    class allPendingTransactions(Resource):
        def get(self):
            x = app.config['DB']
            conn, cursor = x.startQuery()
            x = x.all_pending_transactions(cursor, conn)
            print 'all pending transactions: '
            print x
            return x

    api.add_resource(transaction, '/transaction')
    api.add_resource(allPendingTransactions, '/everythingInTransactions')
    api.add_resource(everythingInDB, '/everythingInDB')
    api.add_resource(everythingInLogger, '/everythingInLogger')

    return app
