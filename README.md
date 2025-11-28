# 🎸 Guitar Pedal BOM Manager

A robust Python tool designed to automate the chaotic process of sourcing electronic components for DIY guitar pedals.

It aggregates messy, inconsistent Bill of Materials (BOM) text from various sources, cleans the data using Regex, performs statistical verification to ensure data integrity, and calculates a "Smart Shopping List" based on safety stock principles.

> **Note:** This repository contains the *software tooling* developed to support a larger hardware engineering project. If you are interested in the circuit builds, schematics, and spectral analysis of the pedals themselves, please visit the companion repository: **[Analog Signal Processing](https://github.com/yourusername/analog-signal-processing)** (Link this when ready).

---

## 🚀 The Problem
Ordering parts for multiple analog circuits is error-prone.
* **Format Inconsistency:** Every BOM uses different spacing, tabs, and naming conventions.
* **Inventory Risk:** Forgetting a single $0.01 resistor costs $15.00 in shipping.
* **Obsolete Parts:** Modern builds often require SMD adaptations (e.g., JFETs like 2N5457) that are easily overlooked.

## 🛠 The Solution
This tool treats BOM parsing as a data reduction problem. It doesn't just read lines; it verifies them.

### Key Features
1.  **Regex Parsing Engine:** Robust pattern matching extracts Designators (R1, C1) and Values (100k, 10uF) regardless of source formatting.
2.  **Residual Analysis:** A verification step inspired by astrophysical data reduction. The script logs every line it *fails* to parse and scans them for "suspicious" content (numbers/keywords). If a part is missed, the system flags it.
3.  **Logic Injection:** The parser identifies specific components (e.g., Through-hole JFETs, DIP ICs) and automatically injects required hardware (SMD Adapter boards, IC Sockets) into the shopping list.
4.  **"Nerd Economics":** Automatically calculates purchase quantities based on component risk and price.
    * *Resistors:* Buffer +5 (Minimum 10).
    * *ICs:* Buffer +1 (Backup).
    * *Passives:* Buffer +3.

---

## 📦 Project Structure
```text
pedal-bom-manager/
├── data/                  <-- Input: Place raw text files here (e.g., rat.txt)
├── src/
│   └── bom_lib.py         <-- Logic: Regex engine, verification, and buying rules
├── output/                <-- Output: Generated CSVs and Checklists
├── app.py                 <-- Interface: Streamlit Web App
├── cli.py                 <-- Interface: Command Line Tool
├── requirements.txt       <-- Dependencies
└── README.md
```

---

## 💻 Usage

### Option 1: The Web Interface (Streamlit)

The easiest way to use the tool is via the browser-based UI.

1.  Install dependencies:
```bash
    pip install -r requirements.txt
```
2.  Launch the app:
```bash
    streamlit run app.py
```
3.  Paste your BOM text into the window and download your CSV.

### Option 2: The Command Line Tool (CLI)

For batch processing local files.

1.  Place your text files (e.g., `big_muff.txt`) inside the `/data` folder.
2.  Run the script:
```bash
    python cli.py
```
3.  Check the terminal for the Verification Report and the `/output` folder for your list.

---

## 📊 Sample Output (Verification Report)

When running the CLI, the tool provides a detailed report on the integrity of the parsing process:
```text
📂 Found 3 BOM files in 'data':
   - Loaded: big_muff.txt
   - Loaded: rat.txt
   - Loaded: dr_q.txt

--- Starting Execution ---

VERIFICATION REPORT (RESIDUAL ANALYSIS)
========================================
Total Lines Scanned: 183
Parts Extracted:     151
----------------------------------------
✅ SUCCESS: Residuals look like pure noise. No missed parts detected.
========================================

LOGIC INJECTION REPORT (Assumptions Made)
========================================
⚠️  SMD ADAPTERS: Script forced adapters for MMBF5457.
    >> ACTION: Check if your PCB already has SOT-23 pads. If so, don't buy these.
ℹ️  IC SOCKETS: Script forced sockets for all DIP chips.
    >> ACTION: Highly recommended for chip safety.
========================================

✅ CSV saved: output/master_shopping_list.csv
✅ Markdown saved: output/shopping_checklist.md
```

---

## 📝 Generated Artifacts

The tool produces two files in the `/output` directory:

1.  **`master_shopping_list.csv`**: A clean spreadsheet sorted by component priority (PCBs -> ICs -> Passives). Includes a "Notes" column with auto-generated warnings.
2.  **`shopping_checklist.md`**: A GitHub-ready markdown table with checkboxes for tracking your order status.

---

## 🔧 Installation & Setup

**Prerequisites:** Python 3.10+
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/pedal-bom-manager.git

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## License

MIT