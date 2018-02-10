# steup
* make a mysql database named idk
* make a table in db named idkman
* table should just have var char or 50+ I called it name
* set hosl, user, passsword, db name database.py
* python app.py
* once running 
* python testTransaction.py
* if you change proccessA and proccessB to run 80 as oppose to current 60 I get: DatabaseError: 1040: Too many connections
* if there  are too many connections then xid key will not save in logger due to error and transaction wont be used 
* but ironically xa recover: will not hold transactions they are never started due to connection error

# what I found 
* regardless if using db pool there is still a connection limit
* now with proccessB I actually created all the transactions and then clearned them later, Now that would only happen if
* it took a long long time for the gateway to determine rollback or commit, or if gatway went down
* now if connection limit were reached we could just spin up a new instance of the appto handle everything else once max connections used???
* basically this error happens when pooled connections are not put back in pool and they arent put back in pool unless gatways lets us know to rollback or commit
