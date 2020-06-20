import json
import random
import time

import requests

from consts import GAME_URL, REQUEST_TIMEOUT, MAX_CARD_ON_PAGE
from src.auth.live_logins import authenticated_accounts
from src.web_app.helper_functions import get_auction_data
from utils.exceptions import TimeoutError, UnknownError, ExpiredSession, Conflict, TooManyRequests, Captcha, PermissionDenied, MarketLocked, TemporaryBanned, \
    NoTradeExistingError


# this class will be vreated ouside the fab loop -> the decorator of the /start-fab will insure that the account is authenticated


class WebappActions:
    def __init__(self, ea_account):
        self.login_instance = authenticated_accounts.get(ea_account)
        self.host = self.login_instance.fut_host
        self.request_session = self.login_instance.request_session
        self.pin = self.login_instance.pin
        self.request_count = 0
        self.credits = 0
        self.duplicates = 0

    def _web_app_request(self, method, url, data=None, params=None):
        self.request_count += 1
        data = data or {}
        params = params or {}
        url = f'https://{self.host}/{GAME_URL}/{url}'
        # respect min wait time between requests
        time.sleep(random.uniform(1.1, 2.5))
        self.request_session.options(url, params=params)

        res = None
        try:
            if method.upper() == 'GET':
                res = self.request_session.get(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'POST':
                res = self.request_session.post(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'PUT':
                res = self.request_session.put(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'DELETE':
                res = self.request_session.delete(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            if res is None:
                raise UnknownError(reason="Something went wrong..")

        except requests.exceptions.Timeout as e:
            raise TimeoutError(e)
        operation_status_switcher = {
            401: ExpiredSession,
            409: Conflict,
            429: TooManyRequests,
            458: Captcha,  # todo handle this someday
            461: PermissionDenied,
            460: PermissionDenied,
            494: MarketLocked,
            512: TemporaryBanned,
            521: TemporaryBanned,
            478: NoTradeExistingError

        }
        if not res.ok:
            raise operation_status_switcher.get(res.status_code, UnknownError(res.content))()
        if res.text == '':
            res = {}
        else:
            res = res.json()
        if 'credits' in res and res['credits']:
            self.credits = res['credits']
        if 'duplicateItemIdList' in res:
            self.duplicates = [i['itemId'] for i in res['duplicateItemIdList']]
        return res

    def sendToPile(self, pile, item_id=None):
        if not isinstance(item_id, (list, tuple)):
            item_id = (item_id,)
        data = {"itemData": [{'pile': pile, 'id': i} for i in item_id]}

        res = self._web_app_request('PUT', 'item', data=json.dumps(data))

        if res['itemData'][0]['success']:
            """ emit here from socket io that the item was sent """
            print(f"item {item_id} was sent to transfer list")
        else:
            print(f"failed to list item, reason: {res['itemData'][0]['reason']}")

    def enter_first_transfer_market_search(self):
        self._web_app_request('GET', 'watchlist')
        self.pin.send_hub_transfers_pin_event()
        self.pin.send_transfer_search_pin_event()

    def go_back_to_search(self):
        self.pin.send_transfer_search_pin_event()

    def search_items(self, item_type, level=None, category=None, masked_def_id=None, def_id=None,
                     min_price=None, max_price=None, min_buy=None, max_bin=None,
                     league=None, club=None, position=None, zone=None, nationality=None,
                     rare=False, play_style=None, start=0, page_size=MAX_CARD_ON_PAGE):

        self.pin.send_transfer_search_pin_event()

        params = {
            'start': start,
            'num': page_size,
            'type': item_type
        }

        if level:
            params['lev'] = level
        if category:
            params['cat'] = category
        if masked_def_id:
            params['maskedDefId'] = masked_def_id
        if def_id:
            params['definitionId'] = def_id
        if min_price:
            params['micr'] = min_price
        if max_price:
            params['macr'] = max_price
        if min_buy:
            params['minb'] = min_buy
        if max_bin:
            params['maxb'] = max_bin
        if league:
            params['leag'] = league
        if club:
            params['team'] = club
        if position:
            params['pos'] = position
        if zone:
            params['zone'] = zone
        if nationality:
            params['nat'] = nationality
        if rare:
            params['rare'] = 'SP'
        if play_style:
            params['playStyle'] = play_style

        res = self._web_app_request('GET', 'transfermarket', params=params)

        search_results = [get_auction_data(i) for i in res.get('auctionInfo', ())]
        if search_results:
            self.pin.send_got_search_results_pin_event()
        else:
            self.pin.send_no_results_pin_event()
        return search_results

    def logout(self):
        self.request_session.delete(f'https://{self.host}/ut/auth', timeout=REQUEST_TIMEOUT)