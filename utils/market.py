import time

from consts import elements
from consts.prices.prices_consts import MIN_PRICE
from enums.actions_for_execution import ElementCallback


def enter_transfer_market(element_actions):
    # click on TRANSFERS
    element_actions.execute_element_action(elements.ICON_TRANSFER_BTN, ElementCallback.CLICK)
    # click on search on transfer market
    element_actions.execute_element_action(elements.TRANSFER_MARKET_CONTAINER_BTN, ElementCallback.CLICK)
    time.sleep(1)


def decrease_increase_min_price(element_actions, increase_price):
    # check if price can be decreased
    decrease_btn = element_actions.get_element(elements.DECREASE_MIN_PRICE_BTN)
    can_be_decreased = decrease_btn.is_enabled() if decrease_btn else False
    max_bin_price = element_actions.get_element(elements.MAX_BIN_PRICE_INPUT)
    max_bin = max_bin_price.get_attribute("value") if max_bin_price else str(MIN_PRICE)
    can_be_increased = True if max_bin != str(MIN_PRICE) else False
    # dont increase when max bin is 200
    # increase min price according to the loop counter
    if can_be_increased and increase_price:
        element_actions.execute_element_action(elements.INCREASE_MIN_PRICE_BTN, ElementCallback.CLICK)
    if not increase_price and can_be_decreased:
        element_actions.execute_element_action(elements.DECREASE_MIN_PRICE_BTN, ElementCallback.CLICK)


def reset_player_page_filters(element_actions):
    reset_player_name_filter(element_actions)
    reset_player_quality_filter(element_actions)
    reset_player_position_filter(element_actions)
    reset_player_chem_style_filter(element_actions)
    reset_player_nationality_filter(element_actions)
    reset_player_league_filter(element_actions)
    reset_player_club_filter(element_actions)


def reset_consumables_page_filters(element_actions):
    reset_consumables_quality_filter(element_actions)
    reset_consumables_specific_name_filter(element_actions)


def reset_player_name_filter(element_actions):
    player_name_placeholder_element = element_actions.get_element(elements.PLAYER_NAME_PLACEHOLDER)
    if "has-selection" in player_name_placeholder_element.get_attribute("class"):
        element_actions.execute_element_action(elements.RESET_PLAYER_NAME_X, ElementCallback.CLICK)


def reset_player_quality_filter(element_actions):
    quality_filter_elament = element_actions.get_element(elements.PLAYER_QUALITY_FILTER_BTN)
    if "has-selection" in quality_filter_elament.get_attribute("class"):
        element_actions.execute_element_action(elements.RESET_QUALITY_FILTER_X, ElementCallback.CLICK)


def reset_player_position_filter(element_actions):
    player_position_filter_btn = element_actions.get_element(elements.PLAYER_POSITION_FILTER_BTN)
    if "has-selection" in player_position_filter_btn.get_attribute("class"):
        element_actions.execute_element_action(elements.REST_PLAYER_POSITION_X, ElementCallback.CLICK)


def reset_player_chem_style_filter(element_actions):
    chem_filter_elament = element_actions.get_element(elements.CHEM_STYLE_FILTER_BTN)
    if "has-selection" in chem_filter_elament.get_attribute("class"):
        element_actions.execute_element_action(elements.RESET_CHEM_STYLE_X, ElementCallback.CLICK)


def reset_player_nationality_filter(element_actions):
    player_nationality_filter_btn = element_actions.get_element(elements.PLAYER_NATIONALITY_FILTER_BTN)
    if "has-selection" in player_nationality_filter_btn.get_attribute("class"):
        element_actions.execute_element_action(elements.RESET_PLAYER_NATION_X, ElementCallback.CLICK)


def reset_player_league_filter(element_actions):
    player_league_filter_btn = element_actions.get_element(elements.PLAYER_LEAGUE_FILTER_BTN)
    if "has-selection" in player_league_filter_btn.get_attribute("class"):
        element_actions.execute_element_action(elements.RESET_PLAYER_LEAGUE_X, ElementCallback.CLICK)


def reset_player_club_filter(element_actions):
    player_club_filter_btn = element_actions.get_element(elements.PLAYER_CLUB_FILTER_BTN)
    if "has-selection" in player_club_filter_btn.get_attribute("class"):
        element_actions.execute_element_action(elements.RESET_PLAYER_CLUB_X, ElementCallback.CLICK)


def reset_consumables_quality_filter(element_actions):
    consumables_quality_filter_element = element_actions.get_element(elements.CONSUMABLES_QUALITY_FILTER_BTN)
    if "has-selection" in consumables_quality_filter_element.get_attribute("class"):
        element_actions.execute_element_action(elements.RESET_CONUMABLES_QUALITY_FILTER_X, ElementCallback.CLICK)


def reset_consumables_specific_name_filter(element_actions):
    chem_filter_elament = element_actions.get_element(elements.CONSUMABLE_SPECIFIC_NAME_FILTER_BTN)
    if chem_filter_elament:
        if "has-selection" in chem_filter_elament.get_attribute("class"):
            element_actions.execute_element_action(elements.RESET_CHEM_STYLE_X, ElementCallback.CLICK)


def enter_players_tab(element_actions):
    element_actions.execute_element_action(elements.PLAYERS_TAB_BUTTON, ElementCallback.CLICK)


def enter_consumables_tab(element_actions):
    element_actions.execute_element_action(elements.CONSUMABLES_TAB_BUTTON, ElementCallback.CLICK)
