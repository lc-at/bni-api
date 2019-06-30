import datetime

import requests_html

from . import constants, utils


class IBankSession:
    """Class that handles a session of BNI Internet Banking (mobile).
    To initiate a session, logging in using `login` method is necessary."""

    def __init__(self):
        """Initialize the class, session, etc."""
        self.logged_in = False
        self.session = requests_html.HTMLSession(mock_browser=False)
        self.session.headers['User-Agent'] = constants.REQ_USER_AGENT
        self.ibank_url = constants.BNI_IBANK_URL
        self.ib_account_name = ''
        self.first_url = ''
        self.last_req = None
        self.session_ttl = constants.SESSION_TTL
        self.session_time = None

    def _maintain_referer(self, referer: str) -> None:
        """Update the referer header in session (for browser sim)"""
        self.session.headers['Referer'] = referer

    def _parse_form_inputs(self,
                           inp_elems: list,
                           *,
                           white: list = [],
                           prefix: str = '__') -> dict:
        """Parse input elements into key:value dictionary.
        This is useful when submitting a form. If the form is
        simple, please prefer submitting using `_submit_form` method."""
        rv = {}
        for inp_elem in inp_elems:
            attrs = inp_elem.attrs
            if 'name' in attrs:
                if attrs.get('name').startswith(prefix) \
                        and white and attrs.get('name') not in white:
                    continue
                rv[attrs.get('name')] = attrs.get('value', '')
        return rv

    def _http_req(self,
                  url: str,
                  method='post',
                  *,
                  maintain_referer: bool = True,
                  last_req: bool = True,
                  **kwargs) -> requests_html.HTMLResponse:
        """Send an HTTP request to a URL with option to maintain referer
        header and last request."""
        func = self.session.post
        if method == 'get':
            func = self.session.get
        r = func(url, **kwargs)
        if maintain_referer:
            self._maintain_referer(r.url)
        if last_req:
            self.last_req = r
        return r

    def _submit_form(self, *, white: list = [], prefix: str = '__',
                     add={}) -> None:
        """Submit the default form in BNI's internet banking interface.
        This function has `white` or whitelist keyword argument to eliminate
        another form input that doesn't start with `prefix`"""
        post_data = self._parse_form_inputs(
            self.last_req.html.xpath('//form[@name="form"]//input'),
            white=white,
            prefix=prefix)
        post_data = dict(**post_data, **add)
        form_action = self.last_req.html.xpath(
            '//form[@name="form"]/@action')[0]
        r = self._http_req(form_action, data=post_data)
        self.last_req = r

    def is_session_alive(self) -> None:
        """Needs login. Checks whether the session is still alive,
        based on SESSION_TTL"""
        if not self.session_time:
            return False
        return datetime.datetime.now() < self.session_time

    def login(self, user_id: str, password: str) -> bool:
        """Log in to an account with provided credentials.
        This will begin session time counting."""
        if self.is_session_alive():
            return True
        r = self._http_req(self.ibank_url, 'get')
        login_url = r.html.xpath('//a[@id="RetailUser"]/@href')[0]
        r = self._http_req(login_url, 'get')
        login_url = r.html.xpath('//form[@name="form"]/@action')[0]
        post_data = self._parse_form_inputs(
            r.html.xpath('//form[@name="form"]//input'))
        post_data['CorpId'] = user_id
        post_data['PassWord'] = password
        r = self._http_req(login_url, data=post_data)
        if r.html.xpath('//span[@id="Display_MConError"]'):
            print(r.html.xpath('//span[@id="Display_MConError"]')[0].text)
            return False
        elif r.html.xpath(
                '//span[@id="message"]') and 'login kembali' in r.text:
            print(r.html.xpath('//span[@id="message"]')[0].text)
            return False
        self.logged_in = True
        if self.last_req.html.xpath('//span[@id="CurrentProfileDisp"]'):
            self.ib_account_name = self.last_req.html.xpath(
                '//span[@id="CurrentProfileDisp"]')[0].text
        self.first_url = r.url
        self.session_time = datetime.datetime.now() + datetime.timedelta(
            seconds=self.session_ttl + 10)
        return True

    def logout(self) -> bool:
        """Needs login. Log out from current session."""
        if not self.is_session_alive():
            return False
        post_data = self._parse_form_inputs(
            self.last_req.html.xpath('//form[@name="form"]//input'))
        post_data.pop('dashBoard', 0)
        r = self._http_req(
            self.last_req.html.xpath('//form[@name="form"]/@action')[0],
            data=post_data)
        post_data = self._parse_form_inputs(
            r.html.xpath('//form[@name="form"]//input'))
        post_data.pop('__BACK__', 0)
        r = self._http_req(r.html.xpath('//form[@name="form"]/@action')[0],
                           data=post_data)
        if 'alasan keamanan' in r.text:
            self.logged_in = False
            self.session_time = None
            return True
        return False

    def get_name(self) -> str:
        """Needs login. Returns associated internet banking account name.
        Please note that internet banking account is different than
        bank account name."""
        if not self.is_session_alive():
            return False
        return self.ib_account_name

    def get_summary(self) -> dict:
        """Needs login. Get bank accounts summary including their corresponding
        general and balance details."""
        if not self.is_session_alive():
            return False
        rv = {'bank_accounts': [], 'total_balance': ''}
        rows = ['general_details', 'balance_details']
        cols = [[
            'bank_account_number', 'short_name', 'name', 'product', 'currency'
        ],
                [
                    'effective_balance', 'blocking_balance',
                    'not_effective_balance', 'interest', 'balance'
                ]]
        post_data = self._parse_form_inputs(
            self.last_req.html.xpath('//form[@name="form"]//input'))
        post_data.pop('LogOut', 0)
        r = self._http_req(
            self.last_req.html.xpath('//form[@name="form"]//@action')[0],
            data=post_data)
        rv['total_balance'] = r.html.xpath(
            '//span[@class="TotalAmt"][last()]')[0].text
        for bank_acc_det in r.html.xpath('//a[contains(@id, "db_acc")]/@href'):
            r = self._http_req(bank_acc_det, 'get')
            d = dict()
            for i in range(2):
                key = rows[i]
                d[key] = dict()
                for j, v in enumerate(cols[i]):
                    td = r.html.xpath(
                        '//table//td[@id="Row{0}_{0}_column2"]'.format(j +
                                                                       1))[i]
                    d[key][v] = td.xpath('//span')[0].text if td.xpath(
                        '//span') else ''
            rv['bank_accounts'].append(d)
        self._submit_form(white=['__HOME__'])
        return rv

    def get_txn_history(self, account_number: str,
                        from_date: datetime.datetime,
                        to_date: datetime.datetime) -> list:
        """Needs login. Get transaction history of a bank account (specified by
        `account_number`) in a specific date range (max is 30 days)."""
        if (to_date - from_date).days >= 30 or (to_date - from_date).days <= 0:
            return False
        from_date = utils.date_to_str(from_date)
        to_date = utils.date_to_str(to_date)
        if not self.is_session_alive():
            return False
        post_data = self._parse_form_inputs(
            self.last_req.html.xpath('//form[@name="form"]//input'))
        post_data.pop("LogOut", 0)
        r = self._http_req(
            self.last_req.html.xpath('//form[@name="form"]//@action')[0],
            data=post_data)
        txn_href = r.html.xpath('//a[@id="TxnHstry"]/@href')[0]
        self._http_req(txn_href, 'get')
        self._submit_form(white=[None], add={'MAIN_ACCOUNT_TYPE': 'OPR'})
        form_action = self.last_req.html.xpath(
            '//form[@name="form"]/@action')[0]
        selected_acc = self.last_req.html.xpath(
            f'//input[contains(@id, "acc") and contains'
            f'(@value, "{account_number}")]/@value')
        if len(selected_acc) < 1:
            breakpoint()
            self._submit_form(white=['__HOME__'])
            raise ValueError("invalid account_number given")
        selected_acc = selected_acc[0]
        post_data = self._parse_form_inputs(
            self.last_req.html.xpath('//form[@name="form"]//input'),
            white=[None])
        post_data['MAIN_ACCOUNT_TYPE'] = 'OPR'
        post_data['Search_Option'] = 'Date'
        post_data['TxnPeriod'] = '-1'
        post_data['txnSrcFromDate'] = from_date
        post_data['txnSrcToDate'] = to_date
        post_data['acc1'] = selected_acc
        r = self._http_req(form_action, data=post_data)
        hists = []
        i = 0
        while i >= 0:
            hist_item = {
                'date': 'Tanggal',
                'description': 'Uraian',
                'type': 'Tipe',
                'amount': 'Nominal',
                'balance': 'Saldo'
            }
            try:
                for k, v in hist_item.copy().items():
                    hist_item[k] = r.html.xpath(
                        f'//table//span[contains(text(), "{v}")]'
                        f'//following::span[1]')[i].text
            except IndexError:
                break
            hists.append(hist_item)
            i += 1
        self._submit_form(white=['__HOME__'])
        return hists
