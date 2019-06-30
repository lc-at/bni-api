from bni_api import IBankSession, utils

user_id = 'YOUR_USER_ID'
password = 'YOUR_PASSWORD'

ib = IBankSession()
ib.login(user_id, password)
print(ib.get_summary()['total_balance'])
ib.logout()
