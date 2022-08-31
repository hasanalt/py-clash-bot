
import code
import os
import random
import sys
import time
from itertools import cycle

import numpy
import pygetwindow
import pyperclip
import PySimpleGUI as sg
from matplotlib import pyplot as plt

from pyclashbot.account import switch_accounts_to
from pyclashbot.auto_update import auto_update
from pyclashbot.battlepass import check_if_can_collect_bp, collect_bp
from pyclashbot.board_scanner import find_enemy_2
from pyclashbot.card_mastery import (check_if_has_mastery_rewards,
                                     collect_mastery_rewards)
from pyclashbot.chest import check_if_has_chest_unlocking, open_chests
from pyclashbot.client import check_quit_key_press, orientate_memu
from pyclashbot.configuration import create_config_file, load_user_settings
from pyclashbot.donate import click_donates, getto_donate_page
from pyclashbot.fight import (check_if_past_game_is_win, fight_with_deck_list,
                              leave_end_battle_window, start_2v2,
                              wait_for_battle_start)
from pyclashbot.launcher import (initialize_client, orientate_bot_window, 
                                 orientate_memu_multi, 
                                 restart_client)
from pyclashbot.logger import Logger
from pyclashbot.request import (check_if_can_request,
                                request_from_clash_main_menu)
from pyclashbot.state import (check_if_in_a_clan_from_main, check_if_in_battle,
                              check_if_on_clash_main_menu, open_clash,
                              return_to_clash_main_menu,
                              wait_for_clash_main_menu)
from pyclashbot.upgrade import getto_card_page, upgrade_cards_from_main_2


create_config_file()
user_settings = load_user_config()
ssids = cycle(user_settings['selected_accounts'])
launcher_path=cycle(user_settings['MEmu_Multi_launcher_path'])


def main_gui():
    out_text=""
    out_text=out_text+"Py-ClashBot\n"
    out_text=out_text+"Matthew Miglio ~May 2022\n\n"
    out_text=out_text+"Py-ClashBot can farm gold, chests, card mastery and battlepass\n"
    out_text=out_text+"progress by farming 2v2 matches with random teammates.\n\n"

    sg.theme('Material2')
    # defining various things that r gonna be in the gui.
    layout = [
        [sg.Text(out_text)],
        [
        sg.Checkbox('Fight',default=False,key="-Fight-in-"),
        sg.Checkbox('Requesting', default=False, key="-Requesting-in-"),
        sg.Checkbox('Donating',default=False,key="-Donating-in-"),
        sg.Checkbox('Upgrade_cards',default=False,key="-Upgrade_cards-in-"),
        sg.Checkbox('Battlepass_reward_collection', default=False, key="-Battlepass_reward_collection-in-"),
        sg.Checkbox('Card_mastery_collection', default=False, key="-Card_mastery_collection-in-"),
        ],
        # buttons
        [sg.Button('Start'), sg.Button('Help'), sg.Button('Donate')]
    ]
    window = sg.Window('PY-ClashBot', layout)

    # run the gui
    while True:
        event, values = window.read()

        #if window close or exit button click
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        jobs=[]
        if values["-Fight-in-"]:
            jobs.append("Fight")
        if values["-Requesting-in-"]:
            jobs.append("Request")
        if values["-Donating-in-"]:
            jobs.append("Donate")
        if values["-Upgrade_cards-in-"]:
            jobs.append("Upgrade_cards")
        if values["-Battlepass_reward_collection-in-"]:
            jobs.append("Collect_battlepass_rewards")
        if values["-Card_mastery_collection-in-"]:
            jobs.append("Collect_mastery_rewards")

        if event == 'Start':
            window.close()
            main_loop(jobs)
           
    window.close()




def main_loop(jobs):
    # # user vars
    # # these will be specified thru the GUI, but these are the placeholders for
    # # now.
    # card_to_request = "giant"
    # ssids = cycle([1, 2])  # change to which account positions to use
    # enable_donate = True
    # enable_card_mastery_collection = True
    # enable_battlepass_collection = True
    # enable_request = True
    # enable_card_upgrade = True
    # enable_program_auto_update = True

    # loop vars
    # *not user vars, do not change*
    logger = Logger()
    ssid = next(ssids)
    state = "restart"
    loop_count = 0

    while True:
        # will be true if installed update, needs feature to restart program
        # installed_update = auto_update(
        # ) if user_settings['enable_program_auto_update'] else False
        logger.log(f"loop count: {loop_count}")

        if (state == "restart"):
            if restart_state(logger) == "restart":
                restart_state(logger)
            else:
                state="clash_main"
            
        if (state == "clash_main"):
            print("clash_main state")
            if clash_main_state(logger, ssid)=="restart": state ="restart"
            else: state = "request"
            
        if (state == "request"):
            if "Request" in jobs:
                if request_state(logger, user_settings['card_to_request'], user_settings['enable_request'])=="restart": state="restart"
                else: state="donate"
            else: state= "donate"
            
        if (state == "donate"):
            if "Donate" in jobs:
                if donate_state(logger, user_settings['enable_donate'])=="restart":state="restart"
                else: state="upgrade"
            else:
                state="upgrade"
            
        if (state == "upgrade"):
            if ("Upgrade_cards" in jobs):
                if upgrade_state(logger, user_settings['enable_card_upgrade'])=="restart": state="restart"
                else: state="battlepass"
            else:
                state="battlepass"
      
        if (state == "battlepass"):
            if ("Collect_battlepass_rewards" in jobs):
                if battlepass_state(logger, user_settings['enable_battlepass_collection']) == "restart" : state = "restart"
                else: state="card_mastery_collection"
            else:
                state="card_mastery_collection"
        
        if (state == "card_mastery_collection"):
            if ("Collect_mastery_rewards" in jobs):
                if card_mastery_collection_state(logger, ['enable_card_mastery_collection']) == "restart": state="restart"
                else: state= "start_fight"
            else: state= "start_fight"
            
        if (state == "start_fight"):
            if ("Fight" in jobs):
                if start_fight_state(logger) == "restart": state="restart"
                else: state="fighting"
            else: state="fighting"
            
        if (state == "fighting"):
            print("fighting state")
            if fighting_state(logger)=="restart": state="restart"
            else: state = "post_fight"
        
        if (state == "post_fight"):
            print("post_fight state")
        ssid, state = post_fight_state(logger, ssids)
        
        loop_count += 1
        user_settings = load_user_settings()
        time.sleep(0.2)







>>>>>>> d2fe85cd915d832e103aaaa0184555483230ee0a

def post_fight_state(logger, ssids):
    logger.log("STATE=post_fight")
    logger.log("Back on clash main")
    if check_if_past_game_is_win(logger):
        logger.log("Last game was a win")
        logger.add_win()
    else:
        logger.log("Last game was a loss")
        logger.add_loss()
        # switch accounts feature

    ssid = next(ssids)
    log = "Next account is: " + str(ssid)
    logger.log(log)
    state = "clash_main"
    return ssid, state


def fighting_state(logger):
    logger.log("-----STATE=fighting-----")
    time.sleep(7)
    fightloops = 0
    while (check_if_in_battle()) and (fightloops < 100):
        check_quit_key_press()
        log = "Plays: " + str(fightloops)
        logger.log(log)
        logger.log("Scanning field.")
        enemy_troop_position = find_enemy_2()
        if enemy_troop_position is not None:
            logger.log(
                f"New enemy position alg found enemy coord to be around {enemy_troop_position[0]},{enemy_troop_position[1]}")
        logger.log("Choosing play.")
        fight_with_deck_list(enemy_troop_position)
        fightloops = fightloops + 1
    logger.log("Battle must be finished")
    time.sleep(10)
    leave_end_battle_window(logger)
    wait_for_clash_main_menu(logger)
    state = "post_fight"
    return state


def start_fight_state(logger):
    logger.log("-----STATE=start_fight-----")
    return_to_clash_main_menu()
    if start_2v2(logger) == "quit":
        # if couldnt find quickmatch button
        logger.log("Had problems finding 2v2 quickmatch button.")
        state = "restart"
    else:
        # if could find the quickmatch button
        if wait_for_battle_start(logger) == "quit":
            # if waiting for battle takes too long
            logger.log(
                "Waited too long for battle start. Restarting")
            state = "restart"
        else:
            # if battle started before wait was too long
            logger.log(
                "Battle has begun. Passing to fighting state")
            state = "fighting"
    return state


def upgrade_state(logger, enable_card_upgrade):
    if not enable_card_upgrade:
        logger.log(
            "Card upgrade is disabled. Passing to card_mastery_collection state.")
        state = "card_mastery_collection"
        return state

    logger.log("-----STATE=upgrade-----")
    # only run upgrade a third of the time because its fucking slow as shit
    # but what can u do yk?
    return_to_clash_main_menu()
    time.sleep(1)
    upgrade_cards_from_main_2(logger)
    time.sleep(1)
    return_to_clash_main_menu()
    logger.log("Finished with upgrading. Passing to card_mastery_collection state")
    state = "card_mastery_collection"
    return state


def card_mastery_collection_state(logger, enable_card_mastery_collection):
    if not enable_card_mastery_collection:
        logger.log(
            "Card_mastery_collection is disabled. Passing to battlepass collection state.")

    logger.log("Getting to card page")
    getto_card_page(logger)
    logger.log("Checking if mastery rewards are available.")
    if check_if_has_mastery_rewards():
        logger.log(
            "Mastery rewards are available. Running mastery collection alg.")
        collect_mastery_rewards(logger)
    logger.log("No mastery rewards are available.")
    logger.log(
        "Done with card mastery collection. Passing to battlepass collection state.")
    state = "battlepass"
    return state


def donate_state(logger, enable_donate):
    if not enable_donate:
        do_upgrade = 1 == random.randint(1, 3)
        if do_upgrade:
            logger.log("Donate is disabled. Passing to upgrade state")
            return "upgrade"
        else:
            logger.log("Donate is disabled. Passing to start_fight state")
            return "start_fight"

    logger.log("-----STATE=donate-----")
    logger.log("Checking if in a clan")
    time.sleep(2)
    do_upgrade = 1 == random.randint(1, 3)
    if check_if_in_a_clan_from_main(logger):
        logger.log("Starting donate alg.")
        time.sleep(2)
        if getto_donate_page(logger) == "quit":
            # if failed to get to clan chat page
            logger.log("Failed to get to clan chat page. Restarting")
            state = "restart"
        else:
            # if got to clan chat page
            logger.log(
                "Successfully got to clan chat page. Starting donate alg")
            click_donates(logger)
            if do_upgrade:
                logger.log("Done with donating. Passing to upgrade state")
                state = "upgrade"
            else:
                logger.log("Done with donating. Passing to start_fight state")
                state = "start_fight"
    else:
        logger.log("You're not in a clan. Skipping donate.")
        if do_upgrade:
            logger.log("Passing to upgrade state")
            state = "upgrade"
        else:
            logger.log("Passing to start_fight state")
            state = "start_fight"
    return state


def request_state(logger, card_to_request, enable_request=True):
    logger.log("State=REQUEST")
    if not enable_request:
        logger.log("Request is disabled. Passing to donate state.")
        return "donate"

    logger.log("-----STATE=request-----")
    logger.log("Trying to get to donate page")
    if getto_donate_page(logger) == "quit":
        # if failed to get to clan chat page
        logger.log("Failed to get to clan chat page. Restarting")
        state = "restart"
    else:
        # if got to clan chat page
        log = "Trying to request " + str(card_to_request) + "."
        logger.log(log)
        if request_from_clash_main_menu(
                card_to_request, logger) == "quit":
            # if request failed
            log = "Failed to request " + str(card_to_request) + "."
            logger.log(log)
        logger.log("Done with requesting. Passing to donate state.")
        return_to_clash_main_menu()
        time.sleep(2)
        state = "donate"
    return state


def clash_main_state(logger, ssid):
    logger.log("-----STATE=clash_main-----")
    # account switch
    logger.log("Logging in to the correct account")
    if switch_accounts_to(logger, ssid) == "quit":
        # if switching accounts fails
        logger.log("Failed to switch accounts. Restarting")
        state = "restart"
    else:
        # if switching accounts works
        logger.log("Successfully switched accounts.")
        # open chests
        if check_if_on_clash_main_menu():
            logger.log(
                "Checking if a chest is being unlocked right now.")
            if not check_if_has_chest_unlocking():
                logger.log(
                    "Found no unlocking symbols. Opening chests.")
                open_chests(logger)
                time.sleep(2)
    



def restart_state(logger):
    logger.log("-----STATE=restart-----")

    restart_client(logger)
    if open_clash(logger) == "quit":
        state = "restart"
    else:
        if check_if_on_clash_main_menu():
            state = "clash_main"
        else:
            state = "restart"
    return state


def battlepass_state(logger, enable_battlepass_collection):
    if not enable_battlepass_collection:
        logger.log(
            "Battlepass collection is disabled. Passing to start_fight state.")

    logger.log("-----STATE=battlepass-----")
    logger.log("Handling battlepass rewards")
    if check_if_can_collect_bp():
        # if we can collect rewards
        logger.log("Battlepass rewards are available.")
        collect_bp(logger)
    else:
        logger.log("Battlepass rewards are unavailable. Continuing to a fight.")
    state = "start_fight"
    return state








def end_loop():
    print("Press ctrl-c to close the program.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    # try:
    #     main_gui()
    # finally:
    #     end_loop()
    
    main_gui()
