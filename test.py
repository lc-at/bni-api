import os
from datetime import datetime

from bni_api import IBankSession, utils

user_id = os.getenv('USER_ID')
password = os.getenv('PASSWORD')

assert user_id and password

now = datetime.now()
assert utils.str_to_date(utils.date_to_str(now))

assert utils.curr_to_int('IDR 12.345.678,00') == 12345678
assert utils.curr_to_int('29.121,00') == 29121

s = IBankSession()

assert s.login('wrong', 'wrong') is False
assert s.is_session_alive() is False

s = IBankSession()

assert s.login(user_id, password)
assert s.is_session_alive()

assert s.get_name() is not None

summary = s.get_summary()
assert summary != {}

assert s.get_txn_history(
    summary['bank_accounts'][0]['general_details']['bank_account_number'],
    utils.str_to_date('01-Jun-2019'),
    utils.str_to_date('30-Dec-2019')) is False

assert s.get_txn_history(
    summary['bank_accounts'][0]['general_details']['bank_account_number'],
    utils.str_to_date('01-Jun-2019'),
    utils.str_to_date('30-Dec-2003')) is False

txn_h = s.get_txn_history(
    summary['bank_accounts'][0]['general_details']['bank_account_number'],
    utils.str_to_date('01-Jun-2019'), utils.str_to_date('30-Jun-2019'))
assert txn_h != []

assert s.logout()
