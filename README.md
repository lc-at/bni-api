# bni-api [![Build Status](https://travis-ci.org/ttycelery/bni-api.svg?branch=master)](https://travis-ci.org/ttycelery/bni-api) [![Known Vulnerabilities](https://snyk.io/test/github/ttycelery/bni-api/badge.svg)](https://snyk.io/test/github/ttycelery/bni-api) [![Maintainability](https://api.codeclimate.com/v1/badges/534cdafc6bac682b7e43/maintainability)](https://codeclimate.com/github/ttycelery/bni-api/maintainability)
To put it into perspective, bni-api is simply a Python wrapper for some of BNI's internet banking functionalities. However, it is not recommended for commercial use. This project is intended for small scale private usage. For commercial use, please prefer using BNI's official API <a href="https://www.bni.co.id/id-id/bisnis/perbankanbisnis/services/otherservices">here</a>.
## Installation
bni-api requires at least Python 3.7 due to the usage of f-strings literal and the `requests-html` module.
To install bni-api, simply run the following command.
```
pip install git+https://git@github.com/ttycelery/bni-api.git@v1.0
```
If you want to install it without pip, clone the repository, then run the following command.
```
python setup.py install
```
## Working Principle
bni-api works by scraping the mobile version of BNI's internet banking website. It uses xpath to select necessary elements that is used to perform an action, thus roughly simulate a real browser session. BNI's internet banking by its nature only allows one session to be running at a time.
### Adding an an extra functionalities
This project only covers some functionalities of BNI's internet banking. Therefore, you need to add your own function if you want more. To do so, you need to understand the working principle and also read the already existed functions so that you won't reinvent the wheel.   

<hr>

# Documentation
Some examples available in `examples` folder. A more detailed explanation about available methods and classes are available in this section.
## bni_api.ibank
This submodule contains ```IBankSession``` which serves its function as session handler.
### IBankSession
```python
IBankSession(self)
```
Class that handles a session of BNI Internet Banking (mobile).
To initiate a session, logging in using `login` method is necessary.
#### is_session_alive
```python
IBankSession.is_session_alive(self) -> None
```
Needs login. Checks whether the session is still alive,
based on SESSION_TTL
#### login
```python
IBankSession.login(self, user_id: str, password: str) -> bool
```
Log in to an account with provided credentials.
This will begin session time counting.
#### logout
```python
IBankSession.logout(self) -> bool
```
Needs login. Log out from current session.
#### get_name
```python
IBankSession.get_name(self) -> str
```
Needs login. Returns associated internet banking account name.
Please note that internet banking account is different than
bank account name.
#### get_summary
```python
IBankSession.get_summary(self) -> dict
```
Needs login. Get bank accounts summary including their corresponding
general and balance details.
#### get_txn_history
```python
IBankSession.get_txn_history(self, account_number: str, from_date: datetime.datetime, to_date: datetime.datetime) -> list
```
Needs login. Get transaction history of a bank account (specified by
`account_number`) in a specific date range (max is 30 days).
## bni_api.utils
This submodule contains some of utilities that might be useful when extracting data from the ```IBankSession``` class.
### str_to_date
```python
str_to_date(s: str) -> datetime.datetime
```
Convert `str` to `datetime.datetime` object. Date format used
here is corresponding to the correct format used in BNI's
internet banking.

### date_to_str
```python
date_to_str(d: datetime.datetime) -> str
```
Convert `datetime.datetime` to `str` object. Date format used
here is corresponding to the correct format used in BNI's
internet banking.

### curr_to_int
```python
curr_to_int(curr: str) -> int
```
Convert a currency formatted `str` to a regular `int`.
This function currently supports only `<currency> <amount>,00`
and `<amount>,00` format.
Conversion of string `IDR 30.000,00` will return `30000`

<hr>

## License
This project is licensed with MIT License.

## Contribution
Feel free to open a new issue or pull request. Any kind of contribution is highly appreciated. If you would like to open a pull request, make sure that it is PEP 8 compliant and have no problems (so that it will pass Travis builds).

## Legal
Disclaimer: This is not affliated, endorsed or certified by BNI. This is an independent and unofficial API. Strictly not for spam. Use at your own risk.
