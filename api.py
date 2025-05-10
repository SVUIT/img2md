from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import PIL.Image
import google.generativeai as genai
import os 
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='.', static_url_path='/app/static',template_folder="static")
CORS(app)

def generate_prompt(have_formula, language):
    if have_formula == 'Yes':
        prompt = f"""
        You are an AI specialized in recognizing hand-written text and mathematical formulas.
        - Extract the handwritten text from the image, ensuring accurate recognition.
        - Correct any grammar mistakes in {language}.
        - Format **math expressions** using **LaTeX inside Markdown**.
        - **DO NOT replace LaTeX expressions with symbols** (e.g., use `\sqrt{{x}}` instead of `√x`).
        - Use:
            - **Inline math**: `$E = mc^2$`
            - **Block math**: `$$\int_0^1 x^2 dx$$`
            - **Fractions**: `\frac{{a}}{{b}}`
            - **Square roots**: `\sqrt{{x}}`
        - **Do NOT add hidden characters or extra spaces in LaTeX expressions.**
        - Return the result in a structured Markdown format, with no additional explanations or introductions.
        """
    elif have_formula == 'No':
        prompt = f"""
        You are an AI specialized in recognizing and processing handwritten text.
        - Extract the handwritten text from the image, ensuring accurate recognition.
        - Correct any grammar mistakes in {language}.
        - Format the output using **Markdown syntax** for better readability.
        - Return the result in a structured Markdown format, with no additional explanations or introductions.
        """
 
    return prompt

def recognize_formula(api_key, language, type_of_text, images):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = generate_prompt(type_of_text, language)
    pil_images = []
    for image in images:
        try:
            img = PIL.Image.open(image)
            pil_images.append(img)
        except Exception as e:
            return f"Error processing image"
    stream = model.generate_content(
        contents= [prompt] + [image for image in pil_images if image],
        # stream=True
    )
    response = stream.text

    response = response.replace("```", '').replace("```markdown", '').replace('markdown','')
    # with open('result.md', "w", encoding="utf-8") as file:
    #     file.write(response)
    lines = response.split("\n")
    formatted_response = "\n".join(line.rstrip() + "  " for line in lines)
    return formatted_response

@app.route('/api/recognize', methods=['POST'])
def recognize():
    api_key = request.form.get('api_key')
    language = request.form.get('language')
    type_of_text = request.form.get('have_formula')
    images = request.files.getlist('images')
    response = recognize_formula(api_key, language, type_of_text, images)
    data = {"text": response}
    return jsonify(data)

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"message": "Hello from Flask!"}
    return jsonify(data)

@app.route('/')
def serve_index():
    return render_template('index.html',
                           api_key=os.getenv('API_KEY'), 
                           client_id=os.getenv('CLIENT_ID'), 
                           app_id=os.getenv('APP_ID')) 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860, debug=True)

