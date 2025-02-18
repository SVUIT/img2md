import google.generativeai as genai
import gradio as gr

def recognize_handwriting(image, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = """
    You are an AI specialized in recognizing handwritten text and mathematical formulas.
    Extract text from the provided handwritten text image and format it in **Markdown**.

    - Use **Markdown syntax** for text formatting.
    - Format **math expressions** using **LaTeX inside Markdown**.
    - **DO NOT replace LaTeX expressions with symbols** (e.g., use `\sqrt{x}` instead of `√x`).
    - Use:
        - **Inline math**: `$E = mc^2$`
        - **Block math**: `$$\int_0^1 x^2 dx$$`
        - **Fractions**: `\frac{a}{b}`
        - **Square roots**: `\sqrt{x}`
    - **Do NOT add hidden characters or extra spaces in LaTeX expressions.**

    Return the result in a structured Markdown format.
    """
    stream = model.generate_content(
        contents= [prompt, image],
        stream=True
    )
    response = ""
    for chunk in stream:
        if chunk.text:
            response +=chunk.text
        yield response

    with open('result.md', "w", encoding="utf-8") as file:
        file.write(response)

view = gr.Interface(
    fn=recognize_handwriting,
    inputs=[gr.Image(type="pil"),gr.Textbox(label="Gemini API key:")],
    outputs=[gr.Markdown(label = "Response:")],
    title="Handwriting Recognition with Gemini",
    description= "Upload an image of handwritten text and get the recognized text. After that, check your markdown file in your folder for the extracted text."
)
if __name__ == '__main__':  
    view.launch(share=True)