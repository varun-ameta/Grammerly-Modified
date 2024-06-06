import openai
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os
from secreatkey import openapi_key

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = openapi_key

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def grammar_and_spelling_check(user_text):
    # Check the word count
    word_count = len(user_text.split())
    
    if word_count > 200:
        return ["Free Word limit exceeded! Upgrade to Premium Version"]
    
    prompt = f"Please remove all the grammatical, spelling, and punctuation errors from the following paragraph and return the corrected paragraph with the number of grammatical, spelling, and punctuation errors separately in new lines.\n{user_text}\n"
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    assistant_response = response.choices[0].message.content
    # Split the response into separate lines
    corrected_lines = assistant_response.split('\n')
    return corrected_lines

def summarize_text(user_text):
    # word_count = len(user_text.split())
    
    # if word_count > 200:
    #     return ["Free Word limit exceeded! Upgrade to Premium Version"]
    
    prompt = f"Please summarize the following text in simple english.\n{user_text}\n"
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    assistant_response = response.choices[0].message.content
    summarized_text= assistant_response
    return summarized_text



def continue_paragraph(user_text):
    # word_count = len(user_text.split())
    
    # if word_count > 200:
    #     return ["Free Word limit exceeded! Upgrade to Premium Version"]
    
    prompt = f"Please complete the following text\n{user_text}\n"
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    assistant_response = response.choices[0].message.content
    completed_text= assistant_response
    return completed_text


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files and request.files['file']:
            # User uploaded a file
            pdf_file = request.files['file']
            if pdf_file and allowed_file(pdf_file.filename):
                # Save the uploaded PDF temporarily
                pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
                pdf_file.save(pdf_file_path)

                # Extract text from the PDF
                user_text = extract_text_from_pdf(pdf_file_path)

                # Delete the temporary PDF file
                os.remove(pdf_file_path)
            else:
                return "Invalid file type. Please upload a PDF file."
        else:
            # User entered text directly
            user_text = request.form.get('user_text', '')

        # Add user's choice
        user_choice = request.form.get('user_choice', 'first')

        if user_choice == 'first':
            corrected_text = grammar_and_spelling_check(user_text)
        elif user_choice == 'second':
            # Summarize the text
            summarized_text = summarize_text(user_text)
            return render_template('index.html', user_text=user_text, summarized_text=summarized_text)
        else:
            # Continue with the paragraph
            continued_text = continue_paragraph(user_text)
            return render_template('index.html', user_text=user_text, continued_text=continued_text)

        return render_template('index.html', user_text=user_text, corrected_text=corrected_text)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    # Create the 'uploads' folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True)
