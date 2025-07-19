# Import necessary libraries
import os
import google.generativeai as genai
from IPython.display import Markdown, display
from dotenv import load_dotenv
import markdown
from weasyprint import HTML

# Load environment variables from .env file
load_dotenv()

# Retrieve the Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Read QlikSense script file (.qvs) as raw text content
with open("sample/SampleQVS1.qvs", "r") as file:
    content = file.read()

# Configure the Gemini API with the provided API key
genai.configure(api_key=GEMINI_API_KEY)

# Read the QlikSense script again (can reuse `content` if optimization needed)
with open("sample/SampleQVS1.qvs", "r") as file:
    qvs_code = file.read()

# Define a detailed prompt instructing the model on how to analyze and explain the QlikSense script
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

"""

# Initialize the Gemini model with a lightweight, cost-effective model
model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")

# Generate explanation by providing instruction and Qlik script to Gemini model
response = model.generate_content([instruction, qvs_code])

# Print a readable header to console for debugging or verification
print("\n========== QlikSense Script Explanation ==========\n")

# Convert markdown response from Gemini to HTML for PDF generation
html_content = markdown.markdown(response.text)

# Generate a PDF report titled "Dashboard Summary.pdf" from the HTML content
HTML(string=html_content).write_pdf("Dashboard Summary.pdf")

# Print completion status
print("done")
