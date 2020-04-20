import datetime

from flask_jwt_extended import create_access_token
from selenium.common.exceptions import TimeoutException

from auth.web_app.auth_status import set_web_app_status, set_auth_status
from auth.web_app.selenium_login import SeleniumLogin
from consts import server_status_messages, app
from ea_account_info.ea_account_actions import update_ea_account_platform, update_ea_account_username, get_ea_account_if_exists, register_new_ea_account
from live_data import active_fabs, ea_account_login_attempts
from utils.driver_functions import get_or_create_driver_instance, close_driver
from utils.elements_manager import ElementActions
from utils.helper_functions import server_response


def start_ea_account_login(owner, email, password):
    # if user exists in db then he must have already logged in before and he has cookies
    existing_ea_account = get_ea_account_if_exists(email, password)

    try:
        driver = get_or_create_driver_instance(email)
        element_actions = ElementActions(driver)
        selenium_login = SeleniumLogin(driver, element_actions)

        if existing_ea_account:
            first_time_login = False
            if not selenium_login.login_with_cookies(password, email, existing_ea_account["cookies"]):
                return server_response(msg=server_status_messages.WEBAPP_FAILED_AUTH, code=401)

        # cookies file was not found - log in the first time
        else:
            first_time_login = True
            if not selenium_login.login_first_time(email, password):
                return server_response(msg=server_status_messages.WEBAPP_FAILED_AUTH, code=401)

            status_code_result = wait_for_status_code_loop(email)
            if not status_code_result:
                return server_response(msg=server_status_messages.LIMIT_TRIES, code=401)

            remember_logged_in_ea_account(owner, driver, email, password)

        # in the web app now get the logged in user details

        element_actions.wait_for_page_to_load_first_time_after_login()

        if not element_actions.check_if_web_app_is_available():
            close_driver(driver, email)
            return server_response(msg=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)

        element_actions.remove_unexpected_popups()
        if first_time_login:
            update_ea_account_platform(email, element_actions)
            update_ea_account_username(email, element_actions)

        set_web_app_status(email, True)
        return server_response(msg=server_status_messages.WEBAPP_SUCCESS_AUTH, code=200)

    except TimeoutException:
        print("Oops :( Something went wrong..")
        return server_response(msg=server_status_messages.FAB_LOOP_FAILED, code=401)
    except Exception as e:
        print(e)
        return server_response(msg=server_status_messages.DRIVER_ERROR, code=503)


def remember_logged_in_ea_account(owner, driver, email, password):
    eaCookies = driver.get_cookies()
    driver.get(app.SIGN_IN_URL)
    signInCookies = driver.get_cookies()

    for cookie in signInCookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        if cookie not in eaCookies:
            eaCookies.append(cookie)

    # update the db
    result = register_new_ea_account(owner, email, password, eaCookies)
    if not result:
        return server_response(msg=server_status_messages.EA_ACCOUNT_ADD_FAILED, code=500)

    set_auth_status(email, True)
    driver.back()


def wait_for_status_code_loop(email):
    while not ea_account_login_attempts[email].is_authenticated:
        if not ea_account_login_attempts[email].tries_with_status_code:
            del active_fabs[email]
            return False
    return True