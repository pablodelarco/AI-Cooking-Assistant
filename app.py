import os
import json
from dotenv import load_dotenv
import openai  

from flask import Flask, render_template, request, jsonify

load_dotenv()

app = Flask(__name__)

# Set the OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/get-recipe", methods=["POST"])
def get_recipe():
    ingredients = request.form["ingredients"].split(", ")
    response_json = chat_with_gpt(ingredients)

    try:
        # Parse the JSON response from ChatGPT
        api_response = json.loads(response_json)

        # Access the list of recipes inside the "recipes" key
        recipes_data = api_response["recipes"]

        # Extract recipes into the desired format
        recipes = [
            {
                "title": recipe["title"],
                "details": recipe["instructions"],
                "source": recipe["source"],  # Include the source URL
            }
            for recipe in api_response["recipes"]
        ]

    except (json.JSONDecodeError, KeyError):
        # Return an error message if parsing fails or expected keys are not found
        return jsonify({"error": "The JSON structure is not as expected."}), 500

    # Render the template with the recipes
    return render_template("index.html", recipes=recipes)


def chat_with_gpt(ingredients):
    ingredients_str = ", ".join(ingredients)
    system_message = {
        "role": "system",
        "content": f"You are a recipe assistant. Provide 5 recipes based on the following ingredients: {ingredients_str} "
        f"Please format the output as JSON with each recipe having a 'title', 'instructions'and 'source'. Source is the link where you found the recipe.",
    }
    # Construct the user input message
    user_input = {
        "role": "user",
        "content": f"I have the following ingredients: {ingredients_str}",
    }
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_input],
        )

        chatbot_response = response.choices[0].message["content"].strip()
        print("ChatGPT response:", chatbot_response)
        return chatbot_response
    except openai.error.OpenAIError as e:
        # Log the error for debugging purposes
        print(f"An error occurred: {e}")
        # Return a custom error message or code
        return "Error: The recipe service is temporarily unavailable. Please try again later."


if __name__ == "__main__":
    app.run(debug=True)
