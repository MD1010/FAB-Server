from items.item_data import build_item_objects_from_dict
from items.item_prices import get_all_items_RT_prices
from items.next_item_to_search import get_next_item_to_search
from user_info.user_actions import update_coin_balance
from utils.market import enter_transfer_market


def execute_pre_run_actions(fab):
    update_coin_balance(fab.user.email, fab.element_actions)
    fab.element_actions.wait_for_page_to_load()
    # get updated rt_prices
    enter_transfer_market(fab.element_actions)


def get_item_to_search_according_to_prices(user_coin_balance, requested_items):
    item_to_search = get_next_item_to_search(user_coin_balance, requested_items)
    if item_to_search is None:
        return None
    return item_to_search


def get_loop_item_for_search(fab, requested_items):
    execute_pre_run_actions(fab)
    requested_items = build_item_objects_from_dict(requested_items)
    requested_items = get_all_items_RT_prices(fab, requested_items)
    item_to_search = get_item_to_search_according_to_prices(fab.user.coin_balance, requested_items)
    return item_to_search
