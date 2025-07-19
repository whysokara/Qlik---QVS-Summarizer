import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import markdown
from weasyprint import HTML
import tempfile

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")

# Set Streamlit page config
st.set_page_config(
    page_title="ScriptSense – Qlik Analyzer",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Light-themed minimalist styling
st.markdown("""
    <style>
        html, body {
            background-color: #f9f9f9;
            font-family: 'Segoe UI', sans-serif;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stApp {
            background-color: #ffffff;
        }
        .css-1v0mbdj, .stTextInput, .stFileUploader {
            border-radius: 12px !important;
        }
        h1, h2, h3 {
            color: #202124;
        }
    </style>
""", unsafe_allow_html=True)

# Brand + Hero Section
st.title("🧠 ScriptSense")
st.subheader("AI-powered QlikSense Script Analyzer")
st.caption("Upload a `.qvs` script. Let Gemini explain everything clearly — like a senior developer would.")

# Upload
uploaded_file = st.file_uploader("📤 Drop your QlikSense `.qvs` file here", type=["qvs"])

if uploaded_file:
    qvs_code = uploaded_file.read().decode("utf-8")

    # Prompt for Gemini
    instruction = """
You are a senior Qlik Sense developer and documentation expert with over 10 years of experience working in complex enterprise environments. Your task is to **analyze the provided Qlik Sense script** (typically written in `.qvs` files or inline within a dashboard) and generate a clear, modular, natural language explanation of the code.

You are assisting a new developer or business analyst who wants to understand what this Qlik dashboard is doing.

---

### 🧠 Your responsibilities:

1. **Explain each section of the script clearly and concisely**, using section headers.
2. If sections are not separated by comments, infer logical breaks (e.g., between loads, joins, variable declarations).
3. Use bullet points to explain each section:
    - What data is being loaded or transformed?
    - Which files/tables/sources are used (QVD, SQL, inline)?
    - What filters, joins, flags, or aggregations are being applied?
    - What KPIs or calculated fields are being derived?
4. Flag **performance bottlenecks or poor practices** (e.g., excessive nested IFs, repeated RESIDENT loads, missing drop statements).
5. Highlight any **data lineage** where a table is loaded from another using RESIDENT.
6. Detect and explain **hidden logic**, such as hardcoded values, synthetic keys, circular references, or cross-table joins.
7. Include **variable explanations**, especially those that drive business logic (like vStartDate, vToday, vRegionFilter).
8. Identify any **dependencies between sections**, such as a load relying on a previously loaded table.
9. Suggest **improvements or best practices** where applicable.
10. Maintain a calm, confident tone — like you're mentoring a junior dev.

---

### 📤 Output Format:

For each logical block or tab in the script, return the following:

#### 📘 Section Title: [Descriptive name, e.g., "Customer Load", "Sales Join", "KPI Calculation"]

- 🔄 **What it does**: Brief one-line summary
- 📂 **Data Source**: QVD / SQL / Inline / Resident etc.
- 🧮 **Fields**: List of fields being loaded or derived
- 🎯 **Filters or Conditions**: Any `WHERE`, `IF`, `Only`, `Match`, etc.
- 🔗 **Joins or Relationships**: If this block depends on another table, explain
- ✏️ **Variables Used**: Mention and explain any variables
- ⚠️ **Warnings or Red Flags**: (if any) Nested IFs, RESIDENT loops, missing drops
- ✅ **Suggestions for Improvement**: (optional)

---

### 📦 Final Summary

At the end of the explanation, generate a **brief summary of the overall logic**, including:
- Main tables used and how they’re joined
- Key KPIs or calculated fields created
- Data refresh logic (e.g., if any incremental loads, loops, or conditional loads)
- Any redundant loads, unused tables, or risky patterns
- Overall data flow: [Data sources] → [Joins/filters] → [KPIs/output tables]

---

### 🧪 Edge Cases to Handle Gracefully:

- Inline loads or temporary flags (e.g., Yes/No flags)
- Set analysis inside variables
- Master calendar generation
- Loop constructs (FOR...NEXT) or script-generated dates
- Variable-based filters that aren't clearly documented
- Hidden synthetic keys or join paths
- Code without comments or poorly structured blocks

---

### ⛔️ Things You Should Not Do:
- Don’t hallucinate code that isn't there.
- Don’t rewrite the code unless explicitly asked.
- Don’t oversimplify — the explanation should be developer-ready.

"""  # Full prompt as you had before

    with st.spinner("Analyzing your QVS file with Gemini..."):
        response = model.generate_content([instruction, qvs_code])
        explanation = response.text
        html_content = markdown.markdown(explanation)

       
       # Extract base filename and create corresponding PDF filename
        base_filename = os.path.splitext(uploaded_file.name)[0]
        pdf_filename = f"{base_filename}.pdf"

        # Generate the PDF into a temp file with user-defined name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            HTML(string=html_content).write_pdf(tmp_pdf.name)
            pdf_path = tmp_pdf.name


        # Output
        st.success("✅ Analysis complete!")
        st.download_button(
            label="📄 Download Full PDF Report",
            data=open(pdf_path, "rb"),
            file_name=pdf_filename,
            mime="application/pdf"
        )

        st.markdown("### 🧾 Gemini Explanation (Preview)", help="Here's what Gemini inferred from your QlikSense script:")
        st.markdown(explanation, unsafe_allow_html=True)

else:
    st.info("Awaiting your `.qvs` script upload to begin analysis.")

# Footer
st.markdown("---")
st.caption("✨ Built with love by [kara](https://x.com/whysokara).. making your Qlik workflows smarter.")
