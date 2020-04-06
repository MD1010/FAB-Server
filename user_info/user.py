from consts import elements
from consts.platform import platforms
from elements.actions_for_execution import ElementCallback
from utils import db


def update_coin_balance(fab):
    fab.user.coin_balance = int(fab.element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))
    db.users_collection.update({"email": fab.user.email}, {"$set": {"coin_balance": fab.user.coin_balance}})


def update_db_user_platform(fab):
    fab.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = fab.element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    db.users_collection.update({"email": fab.user.email}, {"$set": {"platform": platforms[platform_icon_class]}})


def update_db_username(fab):
    fab.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    username = fab.element_actions.get_element(elements.USER_NAME).text
    db.users_collection.update({"email": fab.user.email}, {"$set": {"username": username}})


class User:
    def __init__(self, email, password="", cookies=None):
        if cookies is None:
            cookies = []
        self.email = email
        self.password = password
        self.cookies = cookies
        self.username = ""
        self.platform = ""
        self.total_runtime = 0
        self.coin_balance = 0
        self.total_coins_earned = 0

        # active_users = [{fab,user},{fab,user}]
