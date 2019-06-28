from time import time
import requests_html

__version__ = '1.0'

BNI_IBANK_URL = 'https://ibank.bni.co.id/MBAWeb/FMB'
REQ_USER_AGENT = ('Mozilla/5.0 (Linux; U; Android 2.2)' +
                  ' AppleWebKit/533.1 (KHTML, like Gecko)' +
                  ' Version/4.0 Mobile Safari/533.1')
SESSION_TTL = 5 * 60  # 5 minutes


class IBankSession:
    """Class that handles a session of BNI Internet Banking (mobile)"""

    def __init__(self):
        """Initialize the class, session, etc."""
        self.logged_in = False
        self.session = requests_html.HTMLSession(mock_browser=False)
        self.session.headers['User-Agent'] = REQ_USER_AGENT
        self.ibank_url = BNI_IBANK_URL
        self.ib_account_name = ''
        self.first_url = ''
        self.last_req = None
        self.session_ttl = SESSION_TTL
        self.session_time = None

    def _maintain_referer(self, referer: str) -> None:
        """Update the referer header in session (for browser sim)"""
        self.session.headers['Referer'] = referer

    def _parse_form_inputs(self, inp_elems: list, *, filter=[]) -> dict:
        """Parse input elements into key:value dictionary"""
        rv = {}
        for inp_elem in inp_elems:
            attrs = inp_elem.attrs
            if 'name' in attrs:
                if filter and attrs.get('name') not in filter:
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
        and last request."""
        func = self.session.post
        if method == 'get':
            func = self.session.get
        r = func(url, **kwargs)
        if maintain_referer:
            self._maintain_referer(r.url)
        if last_req:
            self.last_req = r
        return r

    def _submit_form(self, *, white: list = [], prefix: str = '__') -> None:
        post_data = self._parse_form_inputs(
            self.last_req.html.xpath('//form[@name="form"]//input'))
        for k, _ in post_data.copy().items():
            if k.startswith(prefix) and (not white or
                                         (white and k not in white)):
                post_data.pop(k)
        form_action = self.last_req.html.xpath(
            '//form[@name="form"]/@action')[0]
        r = self._http_req(form_action, data=post_data)
        self.last_req = r

    def is_session_alive(self) -> None:
        """Checks whether the session is still alive, based on SESSION_TTL"""
        if not self.session_time:
            return False
        return time() - self.session_time < self.session_ttl

    def login(self, user_id: str, password: str) -> bool:
        """Log in to an account with provided credentials.
        This will begin session time."""
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
        self.session_time = time() - 10
        return True

    def logout(self) -> bool:
        """Log out from current session"""
        if not self.logged_in or not self.last_req \
                or not self.is_session_alive():
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
        """Returns associated account name"""
        return self.ib_account_name

    def get_summary(self) -> dict:
        """Get bank accounts summary including balances"""
        rv = {
            'bank_accounts': {
                'general_details': {},
                'balance_details': {}
            },
            'total_balance': ''
        }
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
            for i in range(2):
                key = rows[i]
                for j, v in enumerate(cols[i]):
                    td = r.html.xpath(
                        '//table//td[@id="Row{0}_{0}_column2"]'.format(j +
                                                                       1))[i]
                    rv['bank_accounts'][key][v] = td.xpath(
                        '//span')[0].text if td.xpath('//span') else ''
        self._submit_form(white=['__HOME__'])
        return rv


if __name__ == '__main__':
    ib = IBankSession()
    breakpoint()
