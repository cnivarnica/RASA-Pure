items = {
    "potion": {"type": "Item", "value": 50, "heal_amount": 20, "description": "A magical potion that heals 20 HP."},
    "sword": {"type": "Weapon", "value": 100, "bonus": 5, "damage": 8, "description": "A sharp sword that increases attack by 5."},
    "armor": {"type": "Armor", "value": 150, "bonus": 3, "description": "Light armor that increases constitution by 3."},
    "mega_sword": {"type": "Weapon", "value": 300, "bonus": 10, "damage": 15, "description": "A powerful sword that greatly increases attack."},
    "health_amulet": {"type": "Accessory", "value": 200, "bonus": 20, "description": "An amulet that increases max HP by 20."}
}

rooms = {
    "village_square": {
        "description": "You're in the village square. There's a shop and a tavern here.",
        "items": ["potion"],
        "npcs": ["merchant", "villager"],
        "exits": {"north": "forest_entrance", "east": "blacksmith", "west": "tavern"},
        "shop": "village_shop"
    },
    "forest_entrance": {
        "description": "You're at the entrance of a dark forest. You can hear strange noises.",
        "items": [],
        "npcs": ["old_man"],
        "exits": {"south": "village_square", "north": "deep_forest"},
        "shop": None
    },
    "deep_forest": {
        "description": "You're in the depths of the forest. It's very dark and eerie.",
        "items": ["health_amulet"],
        "npcs": [],
        "exits": {"south": "forest_entrance", "east": "enchanted_grove"},
        "shop": None,
        "enemies": ["wolf", "ghost_dog"]
    },
    "blacksmith": {
        "description": "You're in the blacksmith's workshop. There are various weapons and armors.",
        "items": [],
        "npcs": ["blacksmith"],
        "exits": {"west": "village_square"},
        "shop": "blacksmith_shop"
    },
    "tavern": {
        "description": "You're in the tavern. It's filled with the chatter of adventurers.",
        "items": [],
        "npcs": ["innkeeper", "drunk_cat"],
        "exits": {"east": "village_square"},
        "shop": "tavern_shop"
    },
    "mountain_pass": {
        "description": "You're on a narrow mountain pass. The wind howls around you.",
        "items": ["climbing_gear"],
        "npcs": ["mountain_guide"],
        "exits": {"south": "village_square", "north": "snowy_peak"},
        "shop": None
    },
    "snowy_peak": {
        "description": "You've reached the snowy peak of the mountain. The view is breathtaking.",
        "items": ["ice_crystal"],
        "npcs": [],
        "exits": {"south": "mountain_pass"},
        "shop": None,
        "enemies": ["frost_giant", "ice_wolf"]
    },
    "enchanted_grove": {
        "description": "You're in a magical grove filled with shimmering plants and glowing mushrooms.",
        "items": ["magic_mushroom"],
        "npcs": ["forest_spirit"],
        "exits": {"west": "deep_forest", "east": "crystal_cave"},
        "shop": None
    },
    "crystal_cave": {
        "description": "You're in a cave filled with glowing crystals of various colors.",
        "items": ["rainbow_crystal"],
        "npcs": ["crystal_miner"],
        "exits": {"west": "enchanted_grove", "down": "underground_city"},
        "shop": "crystal_shop"
    },
    "underground_city": {
        "description": "You've discovered a vast underground city carved into the rock.",
        "items": [],
        "npcs": ["dwarven_king", "gnome_inventor"],
        "exits": {"up": "crystal_cave", "east": "lava_fields"},
        "shop": "dwarven_market"
    },
    "lava_fields": {
        "description": "You're in a hellish landscape of bubbling lava and scorched earth.",
        "items": ["fire_stone"],
        "npcs": [],
        "exits": {"west": "underground_city"},
        "shop": None,
        "enemies": ["fire_elemental", "lava_golem"]
    }
}

enemies = {
    "ghost_dog": {"HP": 3, "STR": 2, "CON": 2, "SPD": 6, "XP": 130, "money": 50, "damage": 8},
    "wolf": {"HP": 2, "STR": 5, "CON": 2, "SPD": 2, "XP": 200, "money": 20, "damage": 5},
    "bandit": {"HP": 50, "STR": 8, "CON": 6, "SPD": 5, "XP": 50, "money": 50, "damage": 10},
    "frost_giant": {"HP": 100, "STR": 12, "CON": 10, "SPD": 4, "XP": 100, "money": 80, "damage": 15},
    "ice_wolf": {"HP": 60, "STR": 8, "CON": 6, "SPD": 9, "XP": 60, "money": 40, "damage": 10},
    "fire_elemental": {"HP": 80, "STR": 10, "CON": 8, "SPD": 7, "XP": 80, "money": 60, "damage": 12},
    "lava_golem": {"HP": 120, "STR": 14, "CON": 12, "SPD": 3, "XP": 120, "money": 100, "damage": 18}
}

npcs = {
    "merchant": {
        "dialogue": "Welcome to my shop! We have the finest goods in the land.",
        "quest": "Fetch me 3 wolf pelts from the deep forest, and I'll reward you handsomely."
    },
    "old_man": {
        "dialogue": "Beware of the dangers that lurk in the deep forest, young one.",
        "quest": "Find my lost amulet in the deep forest, and I'll teach you a powerful spell."
    },
    "blacksmith": {
        "dialogue": "Need any weapons or armor? I've got the best in town!",
        "quest": "Bring me some rare metal from the deep forest, and I'll forge you a legendary weapon."
    },
    "innkeeper": {
        "dialogue": "Welcome to the Purring Pint! Care for a drink or some gossip?",
        "quest": "Help me get rid of the ghost dog in the deep forest, it's scaring away my customers!"
    },
    "drunk_cat": {
        "dialogue": "Hic! Did I ever tell you about the treasure hidden in the deep forest? Hic!",
        "quest": None
    },
    "villager": {
        "dialogue": "It's a peaceful day in the village, isn't it?",
        "quest": None
    },
    "mountain_guide": {
        "dialogue": "Watch your step on the mountain pass. It's treacherous, but the view from the peak is worth it!",
        "quest": "Bring me an ice crystal from the snowy peak, and I'll teach you mountain climbing techniques."
    },
    "forest_spirit": {
        "dialogue": "Welcome to the enchanted grove, traveler. The magic here is ancient and powerful.",
        "quest": "Collect 5 magic mushrooms for me, and I'll grant you the ability to communicate with plants."
    },
    "crystal_miner": {
        "dialogue": "These caves are full of valuable crystals, but be careful. Some say they have a mind of their own.",
        "quest": "Find me a rainbow crystal, and I'll share my secret mining techniques with you."
    },
    "dwarven_king": {
        "dialogue": "Welcome to our underground kingdom, surface dweller. What brings you to the depths?",
        "quest": "Defeat the lava golem that's been threatening our eastern tunnels, and you'll have the gratitude of the dwarven kingdom."
    },
    "gnome_inventor": {
        "dialogue": "Ah, a new test subject! I mean, customer! Want to try my latest invention?",
        "quest": "Bring me 3 fire stones from the lava fields. I need them for my latest invention: fire-proof underwear!"
    }
}

shops = {
    "village_shop": {"items": ["potion", "sword"]},
    "blacksmith_shop": {"items": ["armor", "mega_sword"]},
    "tavern_shop": {"items": ["potion"]},
    "crystal_shop": {"items": ["rainbow_crystal", "ice_crystal"]},
    "dwarven_market": {"items": ["mega_sword", "fire_stone", "climbing_gear"]}
}
