# bni_api

# bni_api.ibank

## IBankSession
```python
IBankSession(self)
```
Class that handles a session of BNI Internet Banking (mobile).
To initiate a session, logging in using `login` method is necessary.
### is_session_alive
```python
IBankSession.is_session_alive(self) -> None
```
Needs login. Checks whether the session is still alive,
based on SESSION_TTL
### login
```python
IBankSession.login(self, user_id: str, password: str) -> bool
```
Log in to an account with provided credentials.
This will begin session time counting.
### logout
```python
IBankSession.logout(self) -> bool
```
Needs login. Log out from current session.
### get_name
```python
IBankSession.get_name(self) -> str
```
Needs login. Returns associated internet banking account name.
Please note that internet banking account is different than
bank account name.
### get_summary
```python
IBankSession.get_summary(self) -> dict
```
Needs login. Get bank accounts summary including their corresponding
general and balance details.
### get_txn_history
```python
IBankSession.get_txn_history(self, account_number: str, from_date: datetime.datetime, to_date: datetime.datetime) -> list
```
Needs login. Get transaction history of a bank account (specified by
`account_number`) in a specific date range (max is 30 days).
# bni_api.utils

## str_to_date
```python
str_to_date(s: str) -> datetime.datetime
```
Convert `str` to `datetime.datetime` object. Date format used
here is corresponding to the correct format used in BNI's
internet banking.

## date_to_str
```python
date_to_str(d: datetime.datetime) -> str
```
Convert `datetime.datetime` to `str` object. Date format used
here is corresponding to the correct format used in BNI's
internet banking.

## curr_to_int
```python
curr_to_int(curr: str) -> int
```
Convert a currency formatted `str` to a regular `int`.
This function currently supports only `<currency> <amount>,00`
and '<amount>,00' format.
Conversion of string 'IDR 30.000,00' will return `30000`

