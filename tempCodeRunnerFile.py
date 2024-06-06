


import openai
from flask import Flask, render_template, request
import PyPDF2

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = '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'

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()
    return text

def grammar_and_spelling_check(user_text):
    # Check the word count
    word_count = len(user_text.split())
    
    if word_count > 200:
        return "Free Word limit exceeded! Upgrade to Premium Version"
    
    prompt = f"Please remove all the grammatical, spelling, and punctuation errors from the following paragraph and return the corrected paragraph with the number of grammatical, spelling, and punctuation errors found in the original paragraph separately.\n{user_text}\n"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    assistant_response = response['choices'][0]['message']['content']
    
    corrected_text_start = assistant_response.find("Corrected Sentences:") + len("Corrected Sentences:")
    corrected_text_end = assistant_response.find("Number of errors found:")
    corrected_text = assistant_response[corrected_text_start:corrected_text_end].strip()
    
    errors_info_start = corrected_text_end + len("Number of errors found:")
    errors_info_end = assistant_response.find("Number of errors found:")
    errors_info = assistant_response[errors_info_start:errors_info_end].strip()
    
    formatted_response = f"Corrected Para - {corrected_text},\n{errors_info}"
    
    return formatted_response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            pdf_file = request.files['file']
            user_text = extract_text_from_pdf(pdf_file)
        else:
            user_text = request.form['user_text']
        
        corrected_text = grammar_and_spelling_check(user_text)
        return render_template('index.html', user_text=user_text, corrected_text=corrected_text)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
