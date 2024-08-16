from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from .custom_actions_packages.rpg_entities import items, rooms, enemies, npcs, shops
import random
import datetime
from dateutil import parser

class ActionStartGame(Action):
    def name(self) -> Text:
        return "action_start_game"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Welcome to RPG Quest! You find yourself in the village square. Type 'look' to see what's around you.")

        return [
            SlotSet("hp", 100),
            SlotSet("max_hp", 100),
            SlotSet("gp", 50),
            SlotSet("xp", 0),
            SlotSet("level", 1),
            SlotSet("str", 10),
            SlotSet("con", 10),
            SlotSet("spd", 10),
            SlotSet("atk", 10),
            SlotSet("inventory", ["potion"]),
            SlotSet("current_room", "village_square"),
            SlotSet("current_quest", None),
            SlotSet("known_spells", []),
            SlotSet("game_state", "exploring"),
            SlotSet("npc", None),
            SlotSet("game_time", "morning")
        ]
#
class ActionMove(Action):
    def name(self) -> Text:
        return "action_move"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(text="You can't move right now.")
            return [SlotSet("direction", None)]

        direction = tracker.get_slot("direction")
        current_room = tracker.get_slot("current_room")

        if current_room not in rooms:
            dispatcher.utter_message(text="You seem to be lost. Returning to the village square.")
            return [SlotSet("current_room", "village_square"), SlotSet("direction", None)]

        if not direction:  # No direction entity provided
            if rooms[current_room]["exits"]:
                buttons = []
                for exit_direction in rooms[current_room]["exits"].keys():
                    buttons.append({"title": exit_direction.capitalize(), "payload": f'/move{{"direction":"{exit_direction}"}}'})
                dispatcher.utter_message(text="Which direction would you like to move?", buttons=buttons)
            else:
                dispatcher.utter_message(text="There are no exits from this room.")
            return []

        if direction in rooms[current_room]["exits"]:
            new_room = rooms[current_room]["exits"][direction]
            dispatcher.utter_message(text=f"You move {direction} to {new_room}.")
            return [SlotSet("current_room", new_room), SlotSet("direction", None), FollowupAction("action_look")]
        else:
            dispatcher.utter_message(text="You can't go that way.")
            return [SlotSet("direction", None)]
#
class ActionLook(Action):
    def name(self) -> Text:
        return "action_look"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            current_room = tracker.get_slot("current_room")
            if current_room in rooms:
                room_info = rooms[current_room]
                message = f"{room_info['description']}\n"
                if room_info.get('items'):
                    message += f"You see: {', '.join(room_info['items'])}.\n"
                if room_info.get('npcs'):
                    message += f"NPCs present: {', '.join(room_info['npcs'])}.\n"
                if room_info.get('enemies'):
                    message += f"Enemies lurking: {', '.join(room_info['enemies'])}.\n"
                if room_info.get('exits'):
                    exits = ', '.join(room_info['exits'].keys())
                    message += f"Exits: {exits}."
                
                time_of_day = tracker.get_slot("game_time")
                message += f"\nIt is currently {time_of_day}."

                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="You seem to be lost. Returning to the village square.")
                return [SlotSet("current_room", "village_square")]
            return []
        except Exception as e:
            print(f"Error in ActionLook: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, I couldn't process that action right now.")
            return []

    def get_time_of_day(self, tracker):
        game_time_str = tracker.get_slot("game_time")
        if not game_time_str:
            return "daytime"
        game_time = parser.parse(game_time_str)
        hour = game_time.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
#
class ActionExplore(Action):
    def name(self) -> Text:
        return "action_explore"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(text="You can't explore right now.")
            return []

        current_room = tracker.get_slot("current_room")
        room_info = rooms.get(current_room, {})

        if random.random() < 0.5:
            found_item = random.choice(room_info.get("items", ["potion"]))
            inventory = tracker.get_slot("inventory") or []
            inventory.append(found_item)
            dispatcher.utter_message(text=f"You found a {found_item}!")
            return [SlotSet("inventory", inventory)]

        elif random.random() < 0.3:
            enemy = random.choice(room_info.get("enemies", ["wolf"]))
            dispatcher.utter_message(text=f"You encounter a {enemy}!")
            return [SlotSet("enemy", enemy), SlotSet("game_state", "in_combat")]

        else:
            material = random.choice(["wood", "stone", "herb"])
            crafting_materials = tracker.get_slot("crafting_materials") or []
            crafting_materials.append(material)
            dispatcher.utter_message(text=f"You found some {material}.")
            return [SlotSet("crafting_materials", crafting_materials)]
#
class ActionStatus(Action):
    def name(self) -> Text:
        return "action_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        hp = tracker.get_slot("hp") or 0
        max_hp = tracker.get_slot("max_hp") or 0
        gp = tracker.get_slot("gp") or 0
        xp = tracker.get_slot("xp") or 0
        level = tracker.get_slot("level") or 1
        next_level_xp = level * 100
        str_stat = tracker.get_slot("str") or 0
        con_stat = tracker.get_slot("con") or 0
        spd_stat = tracker.get_slot("spd") or 0
        atk_stat = tracker.get_slot("atk") or 0
        game_state = tracker.get_slot("game_state")

        message = (f"Character Info:\n"
                   f"Game state: {game_state}\n"
                   f"Level: {level}\n"
                   f"HP: {hp}/{max_hp}\n"
                   f"Money: {gp}\n"
                   f"XP: {xp}\n"
                   f"STR: {str_stat}\n"
                   f"CON: {con_stat}\n"
                   f"SPD: {spd_stat}\n"
                   f"ATK: {atk_stat}\n"
                   f"Progress to next level: {(xp/next_level_xp)*100:.1f}%")

        if game_state == "in_combat":
            enemy = tracker.get_slot("enemy")
            enemy_hp = enemies[enemy]["HP"]
            enemy_str = enemies[enemy]["STR"]
            enemy_con = enemies[enemy]["CON"]
            enemy_spd = enemies[enemy]["SPD"]
            enemy_xp = enemies[enemy]["XP"]
            enemy_money = enemies[enemy]["money"]
            enemy_damage = enemies[enemy]["damage"]
            message += (f"\nIn combat with {enemy} HP: {enemy_hp} "
                        f"\nATK: {enemy_damage} "
                        f"\nSTR: {enemy_str} "
                        f"\nCON: {enemy_con} "
                        f"\nSPD: {enemy_spd} "
                        f"\nXP: {enemy_xp} "
                        f"\nMoney: {enemy_money}")

        dispatcher.utter_message(text=message)
        return []
#
class ActionHelp(Action):
    def name(self) -> Text:
        return "action_help"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        current_room = tracker.get_slot("current_room")

        available_actions = self.get_available_actions(tracker)
        message = "Here are the actions you can take right now:\n\n\n"
        for action in available_actions:
            if " - " in action:
                action_name, action_desc = action.split(" - ", 1)
                message += f"- {action_name} - {action_desc}\n"
            else:
                message += f"- {action}\n"

        message += "\n\nTo perform an action, simply type the action name (e.g. 'look', 'move north', 'attack wolf').\n\n"
        message += "\nIf you're unsure about an action, you can get more information by typing 'help [action]'.\n\n"
        message += "\nHere are some additional tips:\n"
        message += "- Explore different areas to find new items, enemies, and NPCs.\n"
        message += "- Complete quests from NPCs to gain rewards and progress the story.\n"
        message += "- Use items and spells wisely to defeat enemies and survive.\n"
        message += "- Rest at the tavern to fully restore your health.\n"
        message += "- Check your character info to see your current stats and level progress.\n"
        message += "- Craft items from materials you find in the world.\n"
        message += "- Pay attention to your surroundings and the time of day, as they may affect your actions.\n"

        dispatcher.utter_message(text=message)
        return []

    def get_available_actions(self, tracker: Tracker) -> List[Text]:
        available_actions = []
        game_state = tracker.get_slot("game_state")
        if game_state == "exploring":
            available_actions = [
                "look - Examine your surroundings",
                "inventory - Check the items in your inventory",
                "character info - View your character's stats",
                "quest info - See your current quests",
                "move [direction] - Move in the specified direction",
                "shop - Visit the local shop",
                "talk to [npc] - Interact with a non-player character",
                "explore - Search the area for items and enemies",
                "rest - Take a nap to restore health",
                "fish - Try your hand at fishing",
                "mine - Search for rare minerals",
                "craft - Create useful items from materials"
            ]
            current_room = tracker.get_slot("current_room")
            room_info = rooms.get(current_room, {})
            if room_info.get("shop"):
                available_actions.append("buy [item] - Purchase an item from the shop")
            if room_info.get("npcs"):
                available_actions.append(f"talk to [{', '.join(room_info['npcs'])}] - Speak with a specific NPC")
        elif game_state == "in_combat":
            available_actions = [
                "look - Assess the battlefield",
                "inventory - Use an item from your inventory",
                "character info - Check your current status",
                "attack [enemy] - Strike an enemy",
                "use [item] - Consume a usable item",
                "cast [spell] - Unleash a magical spell",
                "run away - Attempt to flee the combat"
            ]
        elif game_state == "shopping":
            available_actions = [
                "look - Inspect the shop's wares",
                "inventory - Review your current items",
                "character info - View your character details",
                "buy [item] - Purchase an item from the shop"
            ]
        elif game_state == "crafting":
            available_actions = [
                "look - Examine your crafting materials",
                "inventory - Check your available items",
                "character info - Review your character stats",
                "craft [item] - Create a new item from your materials"
            ]

        return available_actions
#
class ActionGetItem(Action):
    def name(self) -> Text:
        return "action_get_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(text="You can't pick up items right now.")
            return [SlotSet("item", None)]

        item = tracker.get_slot("item")
        current_room = tracker.get_slot("current_room")
        room_info = rooms.get(current_room, {"items": []})

        if not item:  # No item entity provided
            if room_info["items"]:
                buttons = []
                for item_name in room_info["items"]:
                    buttons.append({"title": item_name.capitalize(), "payload": f'/get_item{{"item":"{item_name}"}}'})
                dispatcher.utter_message(text="Which item would you like to pick up?", buttons=buttons)
            else:
                dispatcher.utter_message(text="There are no items to pick up here.")
            return []

        if item in room_info["items"]:
            inventory = tracker.get_slot("inventory") or []
            inventory.append(item)
            room_info["items"].remove(item)
            dispatcher.utter_message(text=f"You picked up the {item}. {items[item]['description']}")
            return [SlotSet("inventory", inventory), SlotSet("item", None)]
        else:
            dispatcher.utter_message(text=f"There's no {item} here.")
            return [SlotSet("item", None)]

class ActionUseItem(Action):
    def name(self) -> Text:
        return "action_use_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state not in ["exploring", "in_combat"]:
            dispatcher.utter_message(text="You can't use items right now.")
            return [SlotSet("item", None)]

        item = tracker.get_slot("item")
        inventory = tracker.get_slot("inventory") or []

        if not item:  # No item entity provided
            if inventory:
                buttons = []
                for item_name in inventory:
                    buttons.append({"title": item_name, "payload": f'/use_item{{"item":"{item_name}"}}'})
                dispatcher.utter_message(text="Which item would you like to use?", buttons=buttons)
            else:
                dispatcher.utter_message(text="You don't have any items to use.")
            return []

        if item in inventory:
            if item == "potion":
                hp = tracker.get_slot("hp") or 0
                max_hp = tracker.get_slot("max_hp") or 0
                heal_amount = items[item]["heal_amount"]
                hp = min(max_hp, hp + heal_amount)
                inventory.remove(item)
                dispatcher.utter_message(text=f"You used a potion and restored {heal_amount} HP.")
                return [SlotSet("hp", hp), SlotSet("inventory", inventory), SlotSet("item", None)]
            elif items[item]["type"] in ["Weapon", "Armor", "Accessory"]:
                stat = "atk" if items[item]["type"] == "Weapon" else "con" if items[item]["type"] == "Armor" else "max_hp"
                current_stat = tracker.get_slot(stat) or 0
                bonus = items[item]["bonus"]
                new_stat = current_stat + bonus
                dispatcher.utter_message(text=f"You equipped the {item}, gaining {bonus} {stat.upper()} points.")
                return [SlotSet(stat, new_stat), SlotSet("inventory", inventory), SlotSet("item", None)]
            else:
                dispatcher.utter_message(text=f"You can't use the {item} right now.")
                return [SlotSet("item", None)]
        else:
            dispatcher.utter_message(text=f"You don't have a {item} in your inventory.")
            return [SlotSet("item", None)]

class ActionInventory(Action):
    def name(self) -> Text:
        return "action_inventory"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        inventory = tracker.get_slot("inventory") or []
        if inventory:
            message = "Your inventory:\n"
            for item in inventory:
                message += f"- {item}: {items[item]['description']}\n"
        else:
            message = "Your inventory is empty."
        dispatcher.utter_message(text=message)
        return []
#
class ActionShop(Action):
    def name(self) -> Text:
        return "action_shop"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(text="You can't shop right now.")
            return []

        current_room = tracker.get_slot("current_room")
        room_info = rooms.get(current_room, {"shop": None})

        if room_info["shop"]:
            shop_info = shops.get(room_info["shop"], {"items": []})
            message = "Welcome to the shop! Items for sale:\n"
            for item in shop_info['items']:
                message += f"- {item}: {items[item]['value']} GP - {items[item]['description']}\n"
            dispatcher.utter_message(text=message)
            return [SlotSet("game_state", "shopping")]
        else:
            dispatcher.utter_message(text="There's no shop here.")
            return []

class ActionBuyItem(Action):
    def name(self) -> Text:
        return "action_buy_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "shopping":
            dispatcher.utter_message(text="You are not in a shop.")
            return []
        
        item = tracker.get_slot("item")
        current_room = tracker.get_slot("current_room")
        room_info = rooms.get(current_room, {"shop": None})
        gp = tracker.get_slot("gp") or 0

        shop_info = shops.get(room_info["shop"], {"items": []})
        
        if not item:  # No item entity provided
            if shop_info["items"]:
                buttons = []
                for item_name in shop_info["items"]:
                    buttons.append({"title": f"{item_name} ({items[item_name]['value']} GP)", 
                                    "payload": f'/buy_item{{"item":"{item_name}"}}'})
                dispatcher.utter_message(text="What would you like to buy?", buttons=buttons)
            else:
                dispatcher.utter_message(text="There are no items available in this shop.")
            return []

        if item in shop_info["items"]:
            item_cost = items[item]["value"]
            if gp >= item_cost:
                gp -= item_cost
                inventory = tracker.get_slot("inventory") or []
                inventory.append(item)
                dispatcher.utter_message(text=f"You bought {item} for {item_cost} GP.")
                return [SlotSet("gp", gp), SlotSet("inventory", inventory), SlotSet("item", None)]
            else:
                dispatcher.utter_message(text="You don't have enough GP.")
        else:
            dispatcher.utter_message(text="That item is not available in this shop.")
        return [SlotSet("item", None), SlotSet("game_state", "exploring")]

class ActionTrade(Action):
    def name(self) -> Text:
        return "action_trade"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_room = tracker.get_slot("current_room")
        game_state = tracker.get_slot("game_state")
        if current_room != "village_square" and game_state != "exploring":
            dispatcher.utter_message(text="You need to be in the village square to trade.")
            return []

        current_room = tracker.get_slot("current_room")
        if "merchant" not in rooms[current_room].get("npcs", []):
            dispatcher.utter_message(text="There's no one to trade with here.")
            return []

        inventory = tracker.get_slot("inventory") or []
        if not inventory:
            dispatcher.utter_message(text="You don't have anything to trade.")
            return []

        trade_options = {
            "wolf_pelt": 15,
            "magic_crystal": 30,
            "ghost_essence": 50
        }

        message = "Available trades:\n"
        for item, value in trade_options.items():
            message += f"{item}: {value} GP\n"

        dispatcher.utter_message(text=message)
        dispatcher.utter_message(text="What would you like to trade? (Use 'trade [item]' to trade an item)")

        return [SlotSet("game_state", "shopping")]

class ActionExecuteTrade(Action):
    def name(self) -> Text:
        return "action_execute_trade"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "shopping":
            dispatcher.utter_message(text="You're not trading right now.")
            return []

        trade_item = tracker.get_slot("trade_item")
        inventory = tracker.get_slot("inventory") or []
        gp = tracker.get_slot("gp") or 0

        trade_options = {
            "wolf_pelt": 15,
            "magic_crystal": 30,
            "ghost_essence": 50,
            "potion": 25
        }

        if not trade_item:  # No trade_item entity provided
            tradeable_items = [item for item in inventory if item in trade_options]
            if tradeable_items:
                buttons = []
                for item in tradeable_items:
                    buttons.append({"title": f"{item} ({trade_options[item]} GP)", 
                                    "payload": f'/execute_trade{{"trade_item":"{item}"}}'})
                dispatcher.utter_message(text="What would you like to trade?", buttons=buttons)
            else:
                dispatcher.utter_message(text="You don't have any items to trade.")
            return []

        if trade_item in inventory:
            value = items[trade_item]["value"]
            inventory.remove(trade_item)
            gp += value
            dispatcher.utter_message(text=f"You traded {trade_item} for {value} GP.")
            return [SlotSet("inventory", inventory), SlotSet("gp", gp), SlotSet("game_state", "exploring"), SlotSet("trade_item", None)]
        else:
            dispatcher.utter_message(text=f"You don't have a {trade_item} to trade.")
            return [SlotSet("trade_item", None), SlotSet("game_state", "exploring")]

class ActionAttack(Action):
    def name(self) -> Text:
        return "action_attack"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        enemy = tracker.get_slot("enemy")
        current_room = tracker.get_slot("current_room")
        room_info = rooms.get(current_room, {"enemies": []})

        # Start a new combat if not already in combat
        if game_state != "in_combat":
            if not enemy:  # No enemy entity provided
                if room_info["enemies"]:
                    buttons = []
                    for enemy_name in room_info["enemies"]:
                        buttons.append({"title": enemy_name, "payload": f'/attack{{"enemy":"{enemy_name}"}}'})
                    dispatcher.utter_message(text="Which enemy would you like to attack?", buttons=buttons)
                else:
                    dispatcher.utter_message(text="There are no enemies here to attack.")
                return []

            if enemy in room_info.get("enemies", []):
                dispatcher.utter_message(text=f"You engage in combat with the {enemy}!")
                return [SlotSet("game_state", "in_combat"), SlotSet("enemy", enemy)]
            else:
                dispatcher.utter_message(text=f"There's no {enemy} here to attack.")
                return []

        # Continue combat
        if enemy in room_info.get("enemies", []):
            enemy_info = enemies[enemy]
            player_at = tracker.get_slot("atk") or 0
            player_hp = tracker.get_slot("hp") or 0

            damage = max(1, player_at - enemy_info["CON"])
            enemy_info["HP"] -= damage
            message = f"You hit the {enemy} for {damage} damage. "
            if enemy_info["HP"] < 0: enemy_info["HP"] = 0
            message += f"The {enemy} has {enemy_info['HP']} HP remaining.\n"

            if enemy_info["HP"] <= 0:
                xp = tracker.get_slot("xp") or 0
                gp = tracker.get_slot("gp") or 0
                xp += enemy_info["XP"]
                gp += enemy_info["money"]
                message += f"You defeated the {enemy} and gained {enemy_info['XP']} XP and {enemy_info['money']} GP.\n\n\n\n"
                room_info["enemies"].remove(enemy)
                dispatcher.utter_message(text=message)
                return [SlotSet("xp", xp),
                        SlotSet("gp", gp),
                        SlotSet("game_state", "exploring"),
                        SlotSet("enemy", None),
                        FollowupAction("action_check_level_up")]
            else:
                enemy_damage = max(1, enemy_info["damage"] - (tracker.get_slot("con") or 0))
                player_hp -= enemy_damage
                message += f"The {enemy} hits you for {enemy_damage} damage. You have {player_hp} HP left."

                if player_hp <= 0:
                    message += "\nYou have been defeated! Game over."
                    dispatcher.utter_message(text=message)
                    return [SlotSet("hp", 0), SlotSet("game_state", "game_over"), SlotSet("enemy", None)]

            dispatcher.utter_message(text=message)
            return [SlotSet("hp", player_hp), SlotSet("game_state", "in_combat"), SlotSet("enemy", enemy)]
        else:
            dispatcher.utter_message(text=f"There's no {enemy} here to attack.")
            return [SlotSet("game_state", "exploring"), SlotSet("enemy", None)]
#
class ActionRunAway(Action):
    def name(self) -> Text:
        return "action_run_away"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "in_combat":
            dispatcher.utter_message(text="You are not in combat.")
            return []
        success_chance = 0.7
        if random.random() < success_chance:
            dispatcher.utter_message(text="You successfully ran away from the battle.")
            return [SlotSet("game_state", "exploring"), SlotSet("enemy", None)]
        else:
            dispatcher.utter_message(text="You failed to run away. The enemy attacks!")
            return [FollowupAction("action_attack")]
#
class ActionCheckLevelUp(Action):
    def name(self) -> Text:
        return "action_check_level_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        xp = tracker.get_slot("xp") or 0
        level = tracker.get_slot("level") or 1
        if xp >= level * 100:
            dispatcher.utter_message(text="You have enough XP to level up!")
            return [SlotSet("game_state", "leveling_up"), FollowupAction("action_level_up")]
        dispatcher.utter_message(text=f"You need {level * 100 - xp} more XP to level up.")
        return []
#
class ActionLevelUp(Action):
    def name(self) -> Text:
        return "action_level_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        
        if game_state != "leveling_up":
            dispatcher.utter_message(text="You're not currently in a state to level up.")
            return []

        xp = tracker.get_slot("xp") or 0
        level = tracker.get_slot("level") or 1
        next_level_xp = level * 100
        
        level += 1
        xp -= next_level_xp
        dispatcher.utter_message(text=f"Congratulations! You've reached level {level}.\n\n Choose a stat to increase: STR, CON, SPD, or ATK.")
        return [SlotSet("level", level), SlotSet("xp", xp)]
#
class ActionIncreaseStat(Action):
    def name(self) -> Text:
        return "action_increase_stat"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        stat = tracker.get_slot("stat")

        if game_state == "leveling_up":
            if not stat:
                # If no stat is selected, show buttons
                buttons = [
                    {"title": "STR", "payload": '/increase_stat{"stat":"str"}'},
                    {"title": "CON", "payload": '/increase_stat{"stat":"con"}'},
                    {"title": "SPD", "payload": '/increase_stat{"stat":"spd"}'},
                    {"title": "ATK", "payload": '/increase_stat{"stat":"atk"}'}
                ]
                dispatcher.utter_message(text="Which stat would you like to increase?", buttons=buttons)
                return []
            else:
                # Validate the stat name
                valid_stats = ["str", "con", "spd", "atk"]
                if stat.lower() not in valid_stats:
                    dispatcher.utter_message(text=f"'{stat}' is not a valid stat. Please choose one of: {', '.join(valid_stats).upper()}.")
                    return [SlotSet("stat", None)]

                # Increase the stat
                current_value = tracker.get_slot(stat.lower()) or 0
                current_value += 1
                dispatcher.utter_message(text=f"Your {stat.upper()} increased to {current_value}.")
                return [
                    SlotSet(stat.lower(), current_value),
                    SlotSet("game_state", "exploring"),
                    SlotSet("stat", None),  # Clear the stat slot after use
                    FollowupAction("action_check_level_up")
                ]
        else:
            dispatcher.utter_message(text="You are not leveling up right now.")
            return [SlotSet("stat", None)]
#
class ActionQuestInfo(Action):
    def name(self) -> Text:
        return "action_quest_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_quest = tracker.get_slot("current_quest")
        if current_quest:
            dispatcher.utter_message(text=f"Your current quest: {current_quest}")
        else:
            dispatcher.utter_message(text="You don't have any active quests at the moment.")
        return []

class ActionTalkToNPC(Action):
    def name(self) -> Text:
        return "action_talk_to_npc"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        npc = tracker.get_slot("npc")
        current_room = tracker.get_slot("current_room")
        room_info = rooms.get(current_room, {"npcs": []})

        if not npc:  # No entity provided
            if room_info["npcs"]:
                buttons = []
                for npc_name in room_info["npcs"]:
                    buttons.append({"title": npc_name, "payload": f'/talk_to_npc{{"npc":"{npc_name}"}}'})
                dispatcher.utter_message(text="Who would you like to talk to?", buttons=buttons)
            else:
                dispatcher.utter_message(text="There's no one here to talk to.")
            return []

        if npc in room_info["npcs"]:
            npc_info = npcs[npc]
            dialogue = npc_info["dialogue"]
            dispatcher.utter_message(text=f"{npc} says: '{dialogue}'")

            if npc_info.get("quest") and not tracker.get_slot("current_quest"):
                dispatcher.utter_message(text=f"{npc} has a quest for you: {npc_info['quest']}")
                return [SlotSet("current_quest", npc_info["quest"]), SlotSet("npc", None)]
        else:
            dispatcher.utter_message(text=f"There's no {npc} here to talk to.")
        
        return [SlotSet("npc", None)]

class ActionCompleteQuest(Action):
    def name(self) -> Text:
        return "action_complete_quest"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_quest = tracker.get_slot("current_quest")
        inventory = tracker.get_slot("inventory") or []
        
        if not current_quest:
            dispatcher.utter_message(text="You don't have an active quest to complete.")
            return []

        if "wolf pelt" in current_quest.lower() and inventory.count("wolf_pelt") >= 3:
            xp = tracker.get_slot("xp") or 0
            gp = tracker.get_slot("gp") or 0
            xp += 100
            gp += 50
            inventory = [item for item in inventory if item != "wolf_pelt"]
            dispatcher.utter_message(text="You've completed the wolf pelt quest! You gain 100 XP and 50 GP.")
            return [SlotSet("xp", xp), SlotSet("gp", gp), SlotSet("inventory", inventory), SlotSet("current_quest", None)]
        
        elif "lost amulet" in current_quest.lower() and "old_man_amulet" in inventory:
            xp = tracker.get_slot("xp") or 0
            xp += 150
            inventory.remove("old_man_amulet")
            dispatcher.utter_message(text="You've returned the lost amulet! You gain 150 XP and learn a new spell: Fireball!")
            return [SlotSet("xp", xp), SlotSet("inventory", inventory), SlotSet("current_quest", None), SlotSet("known_spells", tracker.get_slot("known_spells") + ["fireball"])]
        
        elif "ghost dog" in current_quest.lower() and "ghost_dog" not in rooms["deep_forest"]["enemies"]:
            xp = tracker.get_slot("xp") or 0
            gp = tracker.get_slot("gp") or 0
            xp += 200
            gp += 100
            dispatcher.utter_message(text="You've defeated the ghost dog! The innkeeper rewards you with 200 XP and 100 GP.")
            return [SlotSet("xp", xp), SlotSet("gp", gp), SlotSet("current_quest", None)]
        
        else:
            dispatcher.utter_message(text="You haven't completed the requirements for your current quest yet.")
            return []

class ActionCastSpell(Action):
    def name(self) -> Text:
        return "action_cast_spell"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        spell = tracker.get_slot("spell")
        known_spells = tracker.get_slot("known_spells") or []
        
        if not spell:  # No spell entity provided
            if known_spells:
                buttons = []
                for spell_name in known_spells:
                    buttons.append({"title": spell_name, "payload": f'/cast_spell{{"spell":"{spell_name}"}}'})
                dispatcher.utter_message(text="Which spell would you like to cast?", buttons=buttons)
            else:
                dispatcher.utter_message(text="You don't know any spells yet.")
            return []
        
        if spell not in known_spells:
            dispatcher.utter_message(text=f"You don't know the {spell} spell.")
            return [SlotSet("spell", None)]
        
        if spell == "fireball":
            if tracker.get_slot("in_combat"):
                enemy = tracker.get_slot("enemy")
                enemy_info = enemies[enemy]
                damage = 20
                enemy_info["HP"] -= damage
                dispatcher.utter_message(text=f"You cast Fireball! The {enemy} takes {damage} damage.")
                if enemy_info["HP"] <= 0:
                    dispatcher.utter_message(text=f"You defeated the {enemy}!")
                    return [SlotSet("in_combat", False), SlotSet("spell", None)]
                else:
                    return [FollowupAction("action_attack"), SlotSet("spell", None)]
            else:
                dispatcher.utter_message(text="You cast Fireball, but there are no enemies around. The spell fizzles out.")
        
        return [SlotSet("spell", None)]

class ActionCraft(Action):
    def name(self) -> Text:
        return "action_craft"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(text="You can't craft right now.")
            return []

        crafting_materials = tracker.get_slot("crafting_materials") or []
        
        if len(crafting_materials) < 3:
            dispatcher.utter_message(text="You don't have enough materials to craft anything.")
            return []

        crafting_materials = crafting_materials[:3]
        inventory = tracker.get_slot("inventory") or []
        inventory.append("potion")
        
        for material in crafting_materials:
            crafting_materials.remove(material)

        dispatcher.utter_message(text="You crafted a potion!")
        return [SlotSet("inventory", inventory), SlotSet("crafting_materials", crafting_materials)]

class ActionFish(Action):
    def name(self) -> Text:
        return "action_fish"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_room = tracker.get_slot("current_room")
        if "river" in rooms[current_room]["description"].lower():
            if random.random() < 0.5:
                fish = random.choice(["trout", "salmon", "catfish"])
                inventory = tracker.get_slot("inventory") or []
                inventory.append(fish)
                dispatcher.utter_message(text=f"You caught a {fish}!")
                return [SlotSet("inventory", inventory)]
            else:
                dispatcher.utter_message(text="You didn't catch anything this time.")
        else:
            dispatcher.utter_message(text="There's no water here to fish in.")
        return []

class ActionMine(Action):
    def name(self) -> Text:
        return "action_mine"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_room = tracker.get_slot("current_room")
        if "cave" in rooms[current_room]["description"].lower():
            if random.random() < 0.4:
                ore = random.choice(["iron", "gold", "diamond"])
                inventory = tracker.get_slot("inventory") or []
                inventory.append(ore)
                dispatcher.utter_message(text=f"You mined some {ore}!")
                return [SlotSet("inventory", inventory)]
            else:
                dispatcher.utter_message(text="You didn't find any valuable ores this time.")
        else:
            dispatcher.utter_message(text="There's nothing to mine here.")
        return []
#
class ActionRest(Action):
    def name(self) -> Text:
        return "action_rest"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state == "in_combat":
            dispatcher.utter_message(text="You can't rest while in combat!")
            return []
        max_hp = tracker.get_slot("max_hp") or 0
        current_room = tracker.get_slot("current_room")
        
        if current_room == "tavern":
            dispatcher.utter_message(text="You take a comfortable nap in the tavern and fully restore your health.")
            return [SlotSet("hp", max_hp), FollowupAction("action_pass_time")]
        else:
            heal_amount = min(max_hp - tracker.get_slot("hp"), 20)
            dispatcher.utter_message(text=f"You rest for a while and recover {heal_amount} HP.")
            return [SlotSet("hp", min(max_hp, (tracker.get_slot("hp") or 0) + heal_amount)), FollowupAction("action_pass_time")]
#
class ActionPassTime(Action):
    def name(self) -> Text:
        return "action_pass_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = tracker.get_slot("game_time")
        time_sequence = ["morning", "afternoon", "evening", "night"]
        current_index = time_sequence.index(current_time)
        new_time = time_sequence[(current_index + 1) % 4]

        dispatcher.utter_message(text=f"Time passes. It is now {new_time}.")

        if new_time == "night":
            dispatcher.utter_message(text="The world feels different at night...")
        elif new_time == "morning":
            dispatcher.utter_message(text="A new day begins, bringing new opportunities.")

        return [SlotSet("game_time", new_time)]
#
class ActionCheckGameOver(Action):
    def name(self) -> Text:
        return "action_check_game_over"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        hp = tracker.get_slot("hp")
        if hp <= 0:
            dispatcher.utter_message(text="Game Over! Your health has reached zero.")
            return [SlotSet("game_state", "game_over")]
        return []
#