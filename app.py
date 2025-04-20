import streamlit as st
import pdfplumber
import re
import pandas as pd
from io import StringIO

st.title("📄 PDF to CSV - MCQ Extractor")

uploaded_file = st.file_uploader("Upload your PDF file with MCQs", type="pdf")

def extract_questions_from_pdf(pdf_file):
    questions = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            pattern = re.compile(
                r'(\d+)\.\s(.*?)\n'  # Question number and text
                r'(A\) .*?\nB\) .*?\nC\) .*?\nD\) .*?\n)'  # Options
                r'(?:Answer|Correct Answer):\s*([A-D])',  # Correct answer
                re.DOTALL
            )
            matches = pattern.findall(text)
            for match in matches:
                q_num, q_text, options, correct_ans = match
                options_split = [opt.strip() for opt in options.strip().split('\n')]
                questions.append({
                    'question_number': q_num,
                    'question_text': q_text.strip(),
                    'Option A': options_split[0][3:],
                    'Option B': options_split[1][3:],
                    'Option C': options_split[2][3:],
                    'Option D': options_split[3][3:],
                    'correct_answer': correct_ans.strip()
                })
    return questions

if uploaded_file:
    with st.spinner("Extracting questions..."):
        data = extract_questions_from_pdf(uploaded_file)
        if data:
            df = pd.DataFrame(data)
            st.success(f"✅ Extracted {len(df)} questions.")
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="questions.csv", mime='text/csv')
        else:
            st.warning("⚠️ No questions found in the PDF. Make sure it's in the correct format.")
