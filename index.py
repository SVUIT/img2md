import google.generativeai as genai
import gradio as gr
import PIL.Image
from datetime import datetime

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

def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"recognition_result_{timestamp}.md"

def recognize_formula(api_key, language, type_of_text, image_files):

    try:
        if not api_key:
            return "Please enter your API key.", None
        if not image_files:
            return "Please upload at least one image.", None
    
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = generate_prompt(type_of_text, language)

        # Process images
        images = []
        for file in image_files:
            try:
                img = PIL.Image.open(file.name)
                images.append(img)
            except Exception as e:
                return f"Error processing image: {str(e)}"

        stream = model.generate_content(
            contents= [prompt] + [image for image in images if image],
            # stream=True
        )

        response = stream.text
        response = response.replace("```", '').replace("```markdown", '').replace('markdown','')
        filename = generate_filename()

        with open(filename, "w", encoding="utf-8") as file:
            file.write(response)

        return response, filename
    
    except Exception as e:
        return f"An error occurred: {str(e)}", None

with gr.Blocks(title="Handwriting Recognition") as view:
    gr.Markdown("# Handwriting Recognition Tool")
    gr.Markdown("Upload images and provide your API key for processing.")
    with gr.Row():
        with gr.Column():
            # API Key input
            api_key_input = gr.Textbox(
                label="Gemini API key:",
                placeholder="Enter your API key here...",
                type="password"
            )

            language = gr.Dropdown(
                choices=["English", "Vietnamese"],
                label="Language"
            )

            have_formula = gr.Dropdown(
                choices=["Yes", "No"],
                label="Have formula?"
            )
            
            # Create image inputs programmatically
            image_files = gr.File(
                file_count="multiple",
                file_types=["image"],
                label="Upload Images"
            )
            # Submit button
            submit_btn = gr.Button("Submit", variant="primary")
            
            help_btn = gr.Button("How to use 🤔", 
                                 variant="huggingface", 
                                 link = "https://github.com/NguyLam2704/img2md/blob/e07ab251e0bd080ee90c293940328a4033f95173/README.md")
        with gr.Column():
            # Output markdown
            gr.Markdown("Response")
            output_markdown = gr.Markdown(label="Response", 
                                          container=True, 
                                          show_label=True, 
                                          line_breaks= True, 
                                          height= 225)

            file_output = gr.File(
                label="Download Markdown File",
                visible=True
            )

    submit_btn.click(
        fn=recognize_formula,
        inputs=[api_key_input, language, have_formula, image_files],
        outputs=[output_markdown, file_output]
    )
if __name__ == '__main__':  
    view.launch(share=True)