import datetime

from bni_api import IBankSession, utils

user_id = 'YOUR_USER_ID'
password = 'YOUR_PASSWORD'

ib = IBankSession()
ib.login(user_id, password)
acct_number = ib.get_summary()['bank_accounts'][0]['bank_account_number']
print(
    ib.get_txn_history(acct_number,
                       datetime.datetime.now() + datetime.timedelta(days=15),
                       datetime.datetime.now()))
ib.logout()
