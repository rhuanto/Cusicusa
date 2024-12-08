import json

def readJson():
    path = 'static/incoming/result/recipes.json'
    jsonData = open(path).read()
    data = json.loads(jsonData)
    titles, ingredients, procedures = [], [], []
    for i in range(len(data)):
        titles.append(data[i]['title'])
        ingredients.append(data[i]['ingredients'])
        procedures.append(data[i]['procedure'])

    ingredients = ['<br>'.join(ing) for ing in ingredients]
    procedures = ['<br>'.join(proc) for proc in procedures]
    return titles, ingredients, procedures