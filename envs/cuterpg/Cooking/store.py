# store.py
from .constant import *
from .utils import singularize, pluralize
from .utils import pluralize

class Store:
    def __init__(self, store_ingredients):
        self.goods = {}
        self.valid_phrases = set()

        for ingredient in store_ingredients:
            self.restock(ingredient)

    def restock(self, 
                product):
        if product in BASE_SEASONINGS or product in SPECIAL_SEASONINGS:
            state = ['standard']
            self.valid_phrases.add(product)
        else:
            state = ['raw']
            self.valid_phrases.add(f"{', '.join(state)} {product}")
        self.goods[product] = {'state': state, 'serving': 100}
        

    def buy(self, character, ingredient_phrase):
        info = ""

        if character.position != 'store':
            return False, "You cannot buy things outside the store."
        
        ingredient_phrase = singularize(ingredient_phrase)

        # Check if the phrase is valid
        if ingredient_phrase not in self.valid_phrases:
            return False, f"The store doesn't have {pluralize(ingredient_phrase)} in stock."

        if ingredient_phrase in SEASONINGS:
            state = 'standard'
            ingredient_name = ingredient_phrase
        else:
            parts = ingredient_phrase.strip().split()
            ingredient_name = parts[-1]
            state = " ".join(parts[:-1])

        info = f"You successfully bought some {pluralize(ingredient_phrase)}."
        if ingredient_phrase in SEASONINGS:
            character.get_ingredient({
                f"{ingredient_name}": {
                    'name': ingredient_name,
                    'state': ['standard'],
                    'serving': 100
                }
            })
        else:
            character.get_ingredient({
                f"raw {ingredient_name}": {
                    'name': ingredient_name,
                    'state': [state],
                    'serving': 100
                }
            })
        return True, info

    def get_store_observation(self):
        phrases = []
        for name, details in self.goods.items():
            state = details['state']
            if 'standard' in state:
                phrases.append(pluralize(name))
            else:
                phrases.append(f"{', '.join(state)} {pluralize(name)}")
        return "In the store, you see " + '; '.join(phrases) + " in stock."
    
