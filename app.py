from flask import Flask, render_template, request
from dotenv import load_dotenv
#from programs.apiCall import apiCall
import google.generativeai as genai
from programs.readJson import readJson
import google.generativeai as genai
import PIL.Image
import json
import os
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/CuisineCapture' , methods=['GET', 'POST'])
def CuisineCapture():
    load_dotenv()
    if request.method == 'POST':
        file = request.files['inputImg']

        file.save('static/incoming/image.jpg')
        #GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        # genai.configure(api_key=GOOGLE_API_KEY)
        genai.configure(api_key='AIzaSyDvnxZy1Azm7utP2DoCR8BasNXd6jiFjJU')

        model = genai.GenerativeModel('gemini-1.5-flash')

        img = PIL.Image.open('static/incoming/image.jpg')

        # Extracting items from the image
        query = '¿puedes identificar los elementos de la imagen que se pueden utilizar para cocinar un plato, no pongas nada excepto los elementos en viñetas?'
        response = model.generate_content([query, img])
        items = response.text.replace("- ", "").split('\n')
        
        itemsStr = ""
        for item in items:
            itemsStr += item + ", "

        query = f'''
         Proporcione tres recetas de comida distintas a partir de los ingredientes estrictamente disponibles en la imagen que incluye {itemsStr} Para cada receta, siga el siguiente formato estructurado:

        Title: Indique claramente el título del plato.
        Ingredients: Enumere todos los ingredientes necesarios.
        Procedure: Instrucciones de cocción paso a paso.
        Asegúrese de que cada receta es única y utiliza los ingredientes especificados en el plato

        Explicación de los cambios:

        Cortesía y claridad: «Sírvase proporcionar» establecer una expectativa educada y clara.
        Numeración: Añadir números (1, 2, 3) proporcionanado una estructura clara, correctamente tabulado,facilitando el seguimiento.
        Detalle de cada sección: Detallar lo que se espera de cada sección (title, ingredients, procedure), solo la etiqueta de la seccion tiene que ser tal cual esta escrito en ingles, garantizar la claridad..
        Singularidad: Especificar que cada receta debe ser «única» fomenta la diversidad de opciones.
        Utilización de ingredientes: Aclarar «utiliza los ingredientes especificados en el plato» garantiza que las recetas se ajusten a las necesidades del usuario.
        En caso de recibir solo un ingrediente agrega algunos ingredientes simples para realizar alguna receta.

        Te dejo un ejemplo de la estructura que quiero:
        
1. **Title:** Bistec a la Plancha Simple

   **Ingredients:**
    * 1 Bistec
    * Sal y Pimienta al gusto
    * Aceite de Oliva

   **Procedure:**
    1. Sazonar el bistec con sal y pimienta por ambos lados.
    2. Calentar una sartén a fuego medio-alto. Agregar una pequeña cantidad de aceite de oliva.
    3. Sellar el bistec durante 2-3 minutos por cada lado para que se dore.
    4. Reducir el fuego a medio y continuar la cocción hasta que alcance el punto de cocción deseado (aproximadamente 3-5 minutos por lado para un bistec medio).
    5. Retirar de la sartén y dejar reposar durante 5 minutos antes de servir.


2. **Title:** Bistec con Salsa de Jugo

   **Ingredients:**
    * 1 Bistec
    * Sal y Pimienta al gusto
    * Aceite de Oliva
    * Agua (1-2 cucharadas)

   **Procedure:**
    1. Sazonar el bistec con sal y pimienta.
    2. Calentar una sartén a fuego alto. Agregar aceite de oliva.
    3. Sellar el bistec por ambos lados a fuego alto.
    4. Reducir el fuego a medio-bajo. Agregar 1-2 cucharadas de agua a la sartén.  Dejar que hierva durante 1-2 minutos para crear una salsa con los jugos de la carne.
    5. Retirar el bistec de la sartén y verter la salsa sobre él antes de servir.


3. **Title:** Bistec Salteado con Cebolla (Asumiendo que hay cebolla disponible)


   **Ingredients:**
    * 1 Bistec
    * 1 Cebolla (Añadiendo este ingrediente para mayor variedad)
    * Sal y Pimienta al gusto
    * Aceite de Oliva

   **Procedure:**
    1. Cortar la cebolla en tiras finas.
    2. Sazonar el bistec con sal y pimienta.
    3. Calentar aceite de oliva en una sartén a fuego medio. Agregar la cebolla y saltearla hasta que esté blanda (unos 5 minutos).
    4. Agregar el bistec a la sartén y cocinarlo hasta que alcance el punto de cocción deseado, revolviendo ocasionalmente para que la cebolla se mezcle con los jugos del bistec.
    5. Servir inmediatamente.

Quiero que siga esa estructura, tabulado como el ejemplo que te estoy dando.
        '''

        response = model.generate_content([query, img])
        print("Respuesta del modelo:", response.text)
        text = response.text
        
        # Split the input text into sections, one for each recipe.
        sections = split_recipes(text)[1:]  # The first split is empty due to the leading split pattern.

        # Extract details from each section.
        recipes = [extract_details(section) for section in sections]

        # Convert the recipes to a JSON string.
        recipes_json = json.dumps(recipes, indent=2)
        path = 'static/incoming/result/recipes.json'
        with open(path, 'w') as file:
            file.write(recipes_json)

        jsonData = open(path).read()
        data = json.loads(jsonData)

        titles, ingredients, procedures = [], [], []
        for i in range(len(data)):
            titles.append(data[i]['title'])
            ingredients.append(data[i]['ingredients'])
            procedures.append(data[i]['procedure'])
        # print(title, ingredients, procedure)
            
        ingredients = ['<br>'.join(ing) for ing in ingredients]
        procedures = ['<br>'.join(proc) for proc in procedures]
    titles, ingredients, procedures = readJson()
    return render_template('CuisineCapture.html', titles=titles, ingredients=ingredients, procedures=procedures, zip=zip)

#app.run(debug=True)