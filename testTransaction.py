import json
import requests
import uuid
from multiprocessing import Process
# import thread


# creates transactions holds them untill
# all are made and then commits or rollsback

def processA():
    TransactionA(60)
    print "process A is completed"


def processB():
    TransactionB(60)
    print "process B is completed"


class TransactionA:

    def __init__(self, amount=1):
        self.xidList = []
        self.commitList = []
        self.deleteList = []
        self.amount = amount
        self.roll = True
        self.init()

    def init(self):
        for x in range(self.amount):
            # theId = uuid.uuid4()
            theId = "A_{}".format(x)  # str(theId)
            self.xidList.append(theId)
        self._startIt()
        print "this is all xids used in transaction a: {}".format(self.xidList)
        print "this is everything in the delete list transaction a: {}".format(
                self.deleteList)
        print "this is everything in the commit list transaction a: {}".format(
                self.commitList)

    def _startIt(self):
        headers = {'Content-Type': 'application/json'}
        for xid in self.xidList:
            urlTransaction = "http://127.0.0.1:5000/transaction"
            r = requests.post(urlTransaction,
                              headers=headers,
                              data=json.dumps({'xid': xid, 'name': xid}))
            # urlEverythingInDB = "http://127.0.0.1:5000/everythingInDB"
            # r = requests.get(urlEverythingInDB, headers=headers)
            # urlEverythingInLogger = "http://127.0.0.1:5000/everythingInLogger"
            # r = requests.get(urlEverythingInLogger, headers=headers)
            if self.roll is True:
                self.roll = False
                urlTransaction = "http://127.0.0.1:5000/transaction?xid={}&action=rollback".format(xid)  # noqa
                r = requests.get(urlTransaction, headers=headers)
                self.deleteList.append(xid)
            else:
                self.roll = True
                urlTransaction = "http://127.0.0.1:5000/transaction?xid={}&action=commit".format(xid)  # noqa
                r = requests.get(urlTransaction, headers=headers)
                self.commitList.append(xid)
            # urlEverything = "http://127.0.0.1:5000/everythingInDB"
            # r = requests.get(urlEverything, headers=headers)
            # urlEverything = "http://127.0.0.1:5000/everythingInLogger"
            # r = requests.get(urlEverything, headers=headers)
            # print "the amount of queries in DB from transaction A= {}".format(r.text)


class TransactionB:

    def __init__(self, amount=1):
        self.xidList = []
        self.deleteList = []
        self.commitList = []
        self.amount = amount
        self.roll = True
        self.init()

    def init(self):
        for x in range(self.amount):
            theId = uuid.uuid1()
            theId = "B_{}".format(x)   # str(theId)
            self.xidList.append(theId)
        self._startIt()
        self._endIt()
        print "all the transaction ids in transaction b: {}".format(
                self.xidList)
        print "everything to be deleted from transaction B: {}".format(
                self.deleteList)
        print "everything to be commited from transaction B: {}".format(
                self.commitList)

    def _startIt(self):
        headers = {'Content-Type': 'application/json'}
        for xid in self.xidList:
            urlTransaction = "http://127.0.0.1:5000/transaction"
            r = requests.post(urlTransaction,
                              headers=headers,
                              data=json.dumps({'xid': xid, 'name': xid}))
            # urlEverythingInDB = "http://127.0.0.1:5000/everythingInDB"
            # r = requests.get(urlEverythingInDB, headers=headers)
            # urlEverythingInLogger = "http://127.0.0.1:5000/everythingInLogger"
            # r = requests.get(urlEverythingInLogger, headers=headers)

    def _endIt(self):
        headers = {'Content-Type': 'application/json'}
        for xid in self.xidList:
            if self.roll is True:
                self.roll = False
                urlTransaction = "http://127.0.0.1:5000/transaction?xid={}&action=rollback".format(xid)  # noqa
                r = requests.get(urlTransaction, headers=headers)
                self.deleteList.append(xid)
            else:
                self.roll = True
                urlTransaction = "http://127.0.0.1:5000/transaction?xid={}&action=commit".format(xid)  # noqa
                r = requests.get(urlTransaction, headers=headers)
                self.commitList.append(xid)

            # urlEverything = "http://127.0.0.1:5000/everythingInDB"
            # r = requests.get(urlEverything, headers=headers)
            # print "here is everything in the DB transaction b: \n".format(r.text)
            # urlEverything = "http://127.0.0.1:5000/everythingInLogger"
            # r = requests.get(urlEverything, headers=headers)
            # print "the amount of queries in DB transaction b= {}".format(r.text)

if __name__ == '__main__':
    p1 = Process(target=processA)
    p1.start()
    # p1.join()
    p2 = Process(target=processB)
    p2.start()
    # p2.join()
