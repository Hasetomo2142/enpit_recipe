from cookpad.recipe_loader import RecipeLoader
import pickle

NUM_RECIPES = 2  # 取得するレシピの数をここで指定します。

with RecipeLoader() as rl:
    recipes_gen = rl.load_all_recipes()
    recipes_list = [next(recipes_gen) for _ in range(NUM_RECIPES)]  # NUM_RECIPESの数だけレシピを取得

with open("sample.pickle", mode="wb") as f:
    pickle.dump(recipes_list, f)


