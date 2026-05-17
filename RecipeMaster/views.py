from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, FirestoreSignUpForm
from .recipe_data import recipe_data_ready, start_recipe_data_download
from django.conf import settings
from django.contrib.auth import login
import os

def loadLines(file_name):
    file_path = os.path.join(settings.RECIPE_DATA_DIR, file_name)
    if not os.path.exists(file_path):
        start_recipe_data_download()
        return []
    with open(file_path, 'r') as file:
        return file.read().splitlines()

def loadUniqueIngredients():
    return loadLines('uniqueIngredients.txt')

def parseOldListLine(line):
    line = line.strip()[4:-4]
    if not line:
        return []
    return line.split('"", ""')

def loadInOrderIngredients():
    file_path = os.path.join(settings.RECIPE_DATA_DIR, 'mostRecentNERLimitRows1.txt')
    file_path2 = os.path.join(settings.RECIPE_DATA_DIR, 'mostRecentNERLimitRows2.txt')

    ingredients_in_order = []
    for file_path in [file_path, file_path2]:
        if not os.path.exists(file_path):
            continue
        with open(file_path, 'r') as file:
            for line in file:
                ingredients_in_order.append(parseOldListLine(line))

    return ingredients_in_order

def loadRecipeNames():
    return loadLines('dishNames.txt')

def isContained(recipeIngredients,userIngredients):
    if(all(x in userIngredients for x in recipeIngredients)):
        return True
    else:
        return False

def loadLinks():
    return loadLines('links.txt')

def makeRecipeLink(link):
    if link.startswith('http://') or link.startswith('https://'):
        return link
    return 'https://' + link

def loadAmounts():
    file_path = os.path.join(settings.RECIPE_DATA_DIR, 'amountsAndIngredients1.txt')
    file_path2 = os.path.join(settings.RECIPE_DATA_DIR, 'amountsAndIngredients2.txt')
    file_path3 = os.path.join(settings.RECIPE_DATA_DIR, 'amountsAndIngredients3.txt')

    amountsList = []
    for file_path in [file_path, file_path2, file_path3]:
        if not os.path.exists(file_path):
            continue
        with open(file_path, "r") as file:
            for line in file:
               if not line.strip():
                   continue
               amountsList.append(parseOldListLine(line))

    return amountsList


@login_required
def displayInitialTemplate(request):
    return render(request, "initial.html")

@login_required
def getDataForLater(request):
    query = request.GET.get('ingredient', '')
    uniqueIngredientNames = loadUniqueIngredients()
    error_message = None
    error_message = request.session.get('error_message', None)
    if request.method == 'POST':
        ingredient = request.POST.get('ingredient')
        if ingredient:
            ingredients = request.session.get('ingredientsForLater', [])
            if ingredient in ingredients:
                error_message = "Ingredient has already been entered"
            else:
                ingredients.append(ingredient)
                request.session['ingredientsForLater'] = ingredients
                return redirect('getDataForLater')
    ingredients = request.session.get('ingredientsForLater', [])
    request.session.pop('error_message', None)  # Removes any previous error message
    return render(request, 'recipeForLater.html', {'query': query, 'uniqueIngredientNames': uniqueIngredientNames, 'ingredients': ingredients, 'error': error_message})

@login_required
def getDataForNow(request):
    query = request.GET.get('ingredient', '')
    uniqueIngredientNames = loadUniqueIngredients()
    error_message = None
    error_message = request.session.get('error_message', None)
    if request.method == 'POST':
        ingredient = request.POST.get('ingredient')
        if ingredient:
            ingredients = request.session.get('ingredients', [])
            if ingredient in ingredients:
                error_message = "Ingredient has already been entered"
            else:
                ingredients.append(ingredient)
                request.session['ingredients'] = ingredients
                return redirect('getDataForNow')
    ingredients = request.session.get('ingredients', [])
    request.session.pop('error_message', None)  # Removes any previous error message
    return render(request, 'recipeForNow.html', {'query': query, 'uniqueIngredientNames': uniqueIngredientNames, 'ingredients': ingredients, 'error': error_message})

@login_required
def submitIngredients(request):
	if not recipe_data_ready():
		start_recipe_data_download()
		message = "Recipe data is still loading. Please try the search again shortly."
		return render(request, 'resultsForNow.html', {'recipes': [], 'message': message})

	ingredients = request.session.get('ingredients', [])
	recipeIngredients = loadInOrderIngredients()
	found = []
	recipes =[]
	message = ""
	count = 0
	for recipe_ingredient_list in recipeIngredients:
		if(len(found) >= 10):
			break
		elif(len(ingredients) < len(recipe_ingredient_list)):
			count += 1
			continue
		elif(isContained(recipe_ingredient_list, ingredients)):
			found.append(count)
			count += 1
			continue
		else:
			count += 1
	recipeNames = loadRecipeNames()
	links = loadLinks()
	amountsOfIngredients = loadAmounts()
	for x in range(len(found)):
		recipe = {
			'name': recipeNames[found[x]],
			'ingredients': recipeIngredients[found[x]],
			'amounts': amountsOfIngredients[found[x]],
			'link': makeRecipeLink(links[found[x]])
		}
		recipes.append(recipe)
	if(len(found) == 0):
		message += "We weren't able to find any recipes that incorporate all the ingredients you listed."
		message += "We recommend removing some ingredients and ensuring you use the auto suggested ingredients to match our records and avoid typos!"
	else:
		message = None

	request.session['recipes'] = recipes
	request.session['message'] = message
	return render(request, 'resultsForNow.html', {'recipes': recipes, 'message': message})

@login_required
def submitIngredientsForLater(request):
	if not recipe_data_ready():
		start_recipe_data_download()
		message = "Recipe data is still loading. Please try the search again shortly."
		return render(request, 'resultsForLater.html', {'recipes': [], 'message': message})

	ingredients = request.session.get('ingredientsForLater', [])
	recipeIngredients = loadInOrderIngredients()
	found = []
	recipes =[]
	message = ""
	count = 0
	for recipe_ingredient_list in recipeIngredients:
		if(len(found) >= 10):
			break
		elif(len(ingredients) >= len(recipe_ingredient_list)):
			count += 1
			continue
		elif(isContained(ingredients, recipe_ingredient_list)):
			found.append(count)
			count += 1
			continue
		else:
			count += 1

	recipeNames = loadRecipeNames()
	links = loadLinks()
	amountsOfIngredients = loadAmounts()
	for x in range(len(found)):
		recipe = {
			'name': recipeNames[found[x]],
			'ingredients': recipeIngredients[found[x]],
			'amounts': amountsOfIngredients[found[x]],
			'link': makeRecipeLink(links[found[x]])
		}
		recipes.append(recipe)
	if(len(found) == 0):
		message += "We weren't able to find any recipes that incorporate all the ingredients you listed."
		message += "We recommend removing some ingredients and ensuring you use the auto suggested ingredients to match our records and avoid typos!"
	else:
		message = None
	request.session['ingredientsForLater'] = []
	request.session['recipes'] = recipes
	request.session['message'] = message
	return render(request, 'resultsForLater.html', {'recipes': recipes, 'message': message})

def clearIngredients(request):
    if 'ingredients' in request.session:
        del request.session['ingredients']
    return redirect('getDataForNow')

def clearIngredientsForLater(request):
    if 'ingredientsForLater' in request.session:
        del request.session['ingredientsForLater']
    return redirect('getDataForLater')

def signUp(request):
    formClass = FirestoreSignUpForm if settings.USE_FIRESTORE_AUTH else SignUpForm
    if(request.method == "POST"):
        form = formClass(request.POST)
        if(form.is_valid()):
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = formClass()
    return render(request, 'signup.html', {'form': form})

@login_required
def showGroceryList(request):
    query = request.GET.get('ingredient', '')
    uniqueIngredientNames = loadUniqueIngredients()
    error_message = None
    if request.method == 'POST':
        ingredient = request.POST.get('ingredient')
        if ingredient:
            ingredients = request.session.get('groceryIngredients', [])
            if ingredient in ingredients:
                error_message = "Ingredient has already been entered"
            else:
                ingredients.append(ingredient)
                request.session['groceryIngredients'] = ingredients
                return redirect('grocery-list')
    ingredients = request.session.get('groceryIngredients', [])

    return render(request, "grocery-list.html", {'query': query, 'uniqueIngredientNames': uniqueIngredientNames, 'ingredients': ingredients, 'error': error_message})

@login_required
def showSavedRecipes(request):
    savedRecipes = request.session.get('savedRecipes', [])
    return render(request, "savedRecipes.html", {'recipes': savedRecipes})

@login_required
def showPantry(request):
    query = request.GET.get('ingredient', '')
    uniqueIngredientNames = loadUniqueIngredients()
    error_message = None
    if request.method == 'POST':
        ingredient = request.POST.get('ingredient')
        if ingredient:
            ingredients = request.session.get('pantryIngredients', [])
            if ingredient in ingredients:
                error_message = "Ingredient has already been entered"
            else:
                ingredients.append(ingredient)
                request.session['pantryIngredients'] = ingredients
                return redirect('pantry')
    ingredients = request.session.get('pantryIngredients', [])
    return render(request, "pantry.html", {'query': query, 'uniqueIngredientNames': uniqueIngredientNames, 'ingredients': ingredients, 'error': error_message})

def removeGroceryIngredient(request):
    ingredient = request.POST.get('ingredient')
    ingredients = request.session.get('groceryIngredients', [])
    if ingredient in ingredients:
        ingredients.remove(ingredient)
        request.session['groceryIngredients'] = ingredients
    return redirect('grocery-list')

def removePantryIngredient(request):
    ingredient = request.POST.get('ingredient')
    ingredients = request.session.get('pantryIngredients', [])
    if ingredient in ingredients:
        ingredients.remove(ingredient)
        request.session['pantryIngredients'] = ingredients
    return redirect('pantry')

def importForLater(request):
    duplicates_found = False
    pantryIngredients = request.session.get('pantryIngredients', [])
    ingredients = request.session.get('ingredientsForLater', [])
    for item in pantryIngredients:
        if item not in ingredients:
            ingredients.append(item)
        else:
            duplicates_found = True
    request.session['ingredientsForLater'] = ingredients

    if duplicates_found:
        request.session['error_message'] = "One or more items weren't imported because they were duplicates."
    else:
        request.session.pop('error_message', None)  # Removes any previous error message

    return redirect('getDataForLater')

def importForNow(request):
    duplicates_found = False
    pantryIngredients = request.session.get('pantryIngredients', [])
    ingredients = request.session.get('ingredients', [])
    for item in pantryIngredients:
        if item not in ingredients:
            ingredients.append(item)
        else:
            duplicates_found = True
    request.session['ingredients'] = ingredients

    if duplicates_found:
        request.session['error_message'] = "One or more items weren't imported because they were duplicates."
    else:
        request.session.pop('error_message', None)  # Removes any previous error message

    return redirect('getDataForNow')

@login_required
def saveRecipe(request):
    name = request.POST.get('recipe_name')
    ingredients = request.POST.get('recipe_ingredients').split(', ')
    link = request.POST.get('recipe_link')
    amounts = request.POST.get('recipe_amounts').split(', ')
    recipe = {
    'name': name,
    'ingredients': ingredients,
    'amounts': amounts,
    'link': link
    }
    savedRecipes = request.session.get('savedRecipes', [])
    savedRecipes.append(recipe)
    request.session['savedRecipes'] = savedRecipes
    message= request.session.get('message')
    recipes = request.session.get('recipes', [])
    return render(request, 'resultsForLater.html', {'recipes': recipes, 'message': message})

@login_required
def saveRecipeForNow(request):
    name = request.POST.get('recipe_name')
    ingredients = request.POST.get('recipe_ingredients').split(', ')
    link = request.POST.get('recipe_link')
    amounts = request.POST.get('recipe_amounts').split(', ')
    recipe = {
    'name': name,
    'ingredients': ingredients,
    'amounts': amounts,
    'link': link
    }
    savedRecipes = request.session.get('savedRecipes', [])
    savedRecipes.append(recipe)
    request.session['savedRecipes'] = savedRecipes
    message= request.session.get('message')
    recipes = request.session.get('recipes', [])
    return render(request, 'resultsForNow.html', {'recipes': recipes, 'message': message})

def clearSavedRecipes(request):
    if 'savedRecipes' in request.session:
        del request.session['savedRecipes']
    return redirect('savedRecipes')

@login_required
def groceryResults(request):
    query = request.GET.get('ingredient', '')
    uniqueIngredientNames = loadUniqueIngredients()
    if request.method == 'POST':
        ingredients = request.session.get('groceryIngredients', [])
        meals = generate_meals(ingredients)
        request.session['meals'] = meals
        return render(request, "grocery-list.html", {'query': query, 'uniqueIngredientNames': uniqueIngredientNames, 'ingredients': ingredients, 'meals':meals})

    ingredients = request.session.get('groceryIngredients', [])
    return render(request, "grocery-list.html", {'query': query, 'uniqueIngredientNames': uniqueIngredientNames, 'ingredients': ingredients})

def generate_meals(ingredients):
	if not recipe_data_ready():
		start_recipe_data_download()
		return []

	recipeIngredients = loadInOrderIngredients()
	found = []
	recipes =[]
	count = 0
	for recipe_ingredient_list in recipeIngredients:
		if(len(found) >= 10):
			break
		elif(len(ingredients) < len(recipe_ingredient_list)):
			count += 1
			continue
		elif(isContained(recipe_ingredient_list, ingredients)):
			found.append(count)
			count += 1
			continue
		else:
			count += 1
	recipeNames = loadRecipeNames()
	links = loadLinks()
	amountsOfIngredients = loadAmounts()
	for x in range(len(found)):
		recipe = {
			'name': recipeNames[found[x]],
			'ingredients': recipeIngredients[found[x]],
			'amounts': amountsOfIngredients[found[x]],
			'link': makeRecipeLink(links[found[x]])
		}
		recipes.append(recipe)
	if(len(found) == 0):
		recipes = []
	return recipes
