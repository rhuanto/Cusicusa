from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image
import json
import os
import re

def split_recipes(text):
    # Split by looking for the number, period, and "Title" keyword.
    # This assumes each recipe starts with "1. Title:", "2. Title:", etc.
    return re.split(r'\d+\.\s+\*\*Title:\*\*', text)

# Function to extract details from each recipe section.
def extract_details(section):
    title_match = re.search(r'(.*?)\n', section)
    ingredients_match = re.search(r'\*\*Ingredients:\*\*(.*?)\*\*Procedure:\*\*', section, re.DOTALL)
    procedure_match = re.search(r'\*\*Procedure:\*\*(.*)', section, re.DOTALL)

    title = title_match.group(1).strip() if title_match else 'No Title Found'
    ingredients = ingredients_match.group(1).strip().split('\n') if ingredients_match else ['No Ingredients Found']
    procedure = procedure_match.group(1).strip().split('\n') if procedure_match else ['No Procedure Found']

    return {
        'title': title,
        'ingredients': [ingredient.strip() for ingredient in ingredients],
        'procedure': [step.strip() for step in procedure]
    }

def apiCall():
    #load_dotenv()
    #GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    #genai.configure(api_key=GOOGLE_API_KEY)
    genai.configure(api_key='AIzaSyDvnxZy1Azm7utP2DoCR8BasNXd6jiFjJU')

    model = genai.GenerativeModel('gemini-pro-vision')
    img = PIL.Image.open('static/incoming/image.jpg')
    query = 'can you identify the items in the image that can be used for cooking a dish, dont put on anything except for the items in bullet points?'
    
    response = model.generate_content([query, img])
    items = response.text.replace("- ", "").split('\n')
    
    itemsStr = ""
    for item in items:
        itemsStr += item + ", "

    query = f'''
    Please provide three distinct food recipes from the ingredients strictly available in the image including {itemsStr} For each recipe, adhere to the following structured format:

    Title: Clearly state the title of the dish.
    Ingredients: List all necessary ingredients.
    Procedure: Step-by-step cooking instructions.
    Ensure each recipe is unique and utilizes the ingredients specified in the dish."

    Explanation of Changes:

    Politeness and Clarity: "Please provide" sets a polite and clear expectation.
    Numbering: Adding numbers (1, 2, 3) provides a clear structure, making it easier to follow.
    Detailing Each Section: Expanding on what is expected in each section (title, ingredients, procedure) ensures clarity.
    Uniqueness: Specifying that each recipe should be "unique" encourages diverse options.
    Ingredient Usage: Clarifying "utilizes the ingredients specified in the dish" ensures the recipes are relevant to the user's needs.
    '''
    response = model.generate_content([query, img])
    text = response.text
    print(text)

    # Split the input text into sections, one for each recipe.
    sections = split_recipes(text)[1:] 

    # Extract details from each section.
    recipes = [extract_details(section) for section in sections]

    # Convert the recipes to a JSON string.
    recipes_json = json.dumps(recipes, indent=2)
    path = 'static/incoming/result/recipes.json'

    with open(path, 'w') as file:
        file.write(recipes_json)