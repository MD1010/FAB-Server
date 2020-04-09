import bcrypt

from live_data import active_fabs
from consts import elements
from consts.platform import platforms
from enums.actions_for_execution import ElementCallback
from models.user import User
from utils import db
from utils.helper_functions import get_coin_balance_from_web_app


def update_coin_balance(email, element_actions):
    current_coin_balance = get_coin_balance_from_web_app(element_actions)
    active_fabs[email].user.coin_balance = current_coin_balance
    db.users_collection.update({"email": email}, {"$set": {"coin_balance": current_coin_balance}})


def update_db_user_platform(email, element_actions):
    element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    db.users_collection.update({"email": email}, {"$set": {"platform": platforms[platform_icon_class]}})


def update_db_username(email, element_actions):
    element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    username = element_actions.get_element(elements.USER_NAME).text
    db.users_collection.update({"email": email}, {"$set": {"username": username}})


def initialize_user_from_db(email):
    user_from_db = db.users_collection.find_one({"email": email})
    return User(email, user_from_db["password"], user_from_db["cookies"], user_from_db["username"], user_from_db["platform"])


def get_user_from_db_if_exists(email, password):
    user_in_db = db.users_collection.find_one({"email": email})
    if not user_in_db:
        return None
    if bcrypt.hashpw(password.encode('utf-8'), user_in_db["password"]) == user_in_db["password"]:
        return user_in_db
    else:
        return None


def get_db_user_platform(email):
    user_in_db = db.users_collection.find_one({"email": email})
    return user_in_db["platform"]


def get_db_username(email):
    user_in_db = db.users_collection.find_one({"email": email})
    return user_in_db["username"]