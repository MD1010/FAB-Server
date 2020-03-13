from selenium.common.exceptions import TimeoutException, WebDriverException

import time
import os.path
from auth.login import set_auth_status, check_auth_status, login_with_cookies, login_first_time, remember_logged_in_user, wait_for_code
from consts.app import AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION
from players.player_buy import decrease_increase_min_price, get_player_to_search, get_sell_price, open_trasfer_market
from consts import app, elements, server_status_messages
from players.players_actions import PlayerActions

from elements.elements_manager import ElementCallback, initialize_element_actions
from driver import initialize_driver
from user_info import user


def get_coin_balance(self):
    coin_balance = self.element_actions.get_element(elements.COIN_BALANCE).text
    return int(coin_balance.replace(',', ''))


def run_loop(self, time_to_run_in_sec, requested_players):
    increase_min_price = True
    num_of_tries = 0
    user.coin_balance = get_coin_balance(self)
    player_to_search = get_player_to_search(requested_players)
    if player_to_search is None:
        return False
    # open_trasfer_market(self)

    start = time.time()
    while True:
        current_coin_balance = get_coin_balance(self)
        if user.coin_balance != current_coin_balance:
            user.coin_balance = current_coin_balance
            player_to_search = get_player_to_search(requested_players)
            if player_to_search is None:
                return False
        search_max_price = str(player_to_search.max_buy_price)
        search_player_name = player_to_search.name
        self.playerActions.init_search_player_info(search_player_name, search_max_price)
        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)

        # give time for the elements in the page to render - if remove stale exception
        time.sleep(1)
        # player_bought = self.playerActions.buy_player()
        player_bought = None

        if player_bought:
            pass
            # list_price = get_sell_price(player_to_search.market_price)
            # self.playerActions.list_player(list_price)
        else:
            self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
        decrease_increase_min_price(self, increase_min_price)
        increase_min_price = not increase_min_price
        curr_time = time.time()
        if curr_time - start > time_to_run_in_sec:
            break
        num_of_tries += 1
        if num_of_tries % AMOUNT_OF_SEARCHES_BEFORE_SLEEP == 0:
            time.sleep(SLEEP_MID_OPERATION_DURATION)

    return True


class Fab:
    def __init__(self):
        self.is_authenticated = False
        self.driver = None
        self.statusCode = ''
        self.element_actions = None
        self.playerActions = None

    def start_login(self, email, password):
        try:
            initialize_driver(self)
            initialize_element_actions(self)
            if os.path.isfile(app.COOKIES_FILE_NAME):
                login_with_cookies(self, password)

            # cookies file was not found - log in the first time
            else:
                login_first_time(self, email, password)
                # can be screwed here, may send bad status here..
                wait_for_code(self)
                remember_logged_in_user(self)
                set_auth_status(self, True)
            return server_status_messages.SUCCESS_AUTH, 200

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            return server_status_messages.FAILED_AUTH, 401

    @check_auth_status
    def start_loop(self, time_to_run_in_sec, requested_players):
        try:
            self.playerActions = PlayerActions(self.driver)
            self.element_actions.wait_for_page_to_load()
            self.element_actions.remove_unexpected_popups()
            result = run_loop(self, time_to_run_in_sec, requested_players)
            if result is True:
                return server_status_messages.FAB_LOOP_FINISHED, 200
            else:
                return server_status_messages.NO_BUDGET_LEFT, 503

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            return server_status_messages.FAB_LOOP_FAILED, 503

    def set_status_code(self, code):
        self.statusCode = code
        return server_status_messages.STATUS_CODE_SET_CORRECTLY, 200
