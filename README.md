# 🎸 Guitar Pedal BOM Manager

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A robust Python tool designed to automate the chaotic process of sourcing electronic components for DIY guitar pedals.

It aggregates messy, inconsistent Bill of Materials (BOM) text from various sources, cleans the data using Regex, performs statistical verification to ensure data integrity, and calculates a "Smart Shopping List" based on safety stock principles.

**🚀 [Try the Live App](https://pedal-bom-manager.streamlit.app/)**

![Demo](assets/demo.gif)

> **Note:** This repository contains the *software tooling* developed to support a larger hardware engineering project. A companion repository featuring the circuit builds, schematics, and spectral analysis of the pedals themselves is currently in development.

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

## 🧠 Engineering Decisions

This project was built to solve a specific reliability problem. Here is the reasoning behind the architectural choices:

### 1. Deterministic Regex over LLMs
While it might be easier to pass BOMs to an LLM (like ChatGPT), non-deterministic outputs are unacceptable for procurement. A hallucinated quantity or part number results in a failed hardware build.
* **Decision:** I implemented a **deterministic Regex parser** to ensure 100% repeatability.
* **Implementation:** The strict pattern matching isolates designators and values, ignoring variable whitespace and human-written descriptions.

### 2. Residual Analysis (Self-Verification)
Drawing from astrophysical data reduction techniques, it is critical to analyze "residuals" (data not fitted by the model) to ensure no signal is lost.
* **The Mechanism:** The script logs every line of text that *fails* the regex match.
* **The Safety Net:** It scans these residuals for "suspicious" content (numbers, keywords like "uF"). If a component is skipped due to formatting errors, the system alerts the user immediately in the terminal.

### 3. Logic Injection for Obsolete Parts
Modern DIY electronics often rely on parts that are now only available in Surface Mount (SMD) formats (e.g., the 2N5457 JFET).
* **The Risk:** Beginners often buy the SMD chip but forget the conversion board, stalling the project.
* **The Solution:** The parser acts as a domain expert. It detects specific obsolete part numbers and **injects** the required adapter hardware into the shopping list automatically.

### 4. Heuristic Safety Stock ("Nerd Economics")
In hardware prototyping, the cost of downtime exceeds the cost of inventory.
* **Decision:** I implemented a **Yield Management Algorithm** that adjusts purchase quantities based on component risk vs. cost.
* **Logic:**
    * **High Risk / Low Cost:** Resistors get a +10 buffer (Cost: ~$0.10. Benefit: Prevents $15 shipping fees for lost parts).
    * **Critical Silicon:** ICs get a +1 buffer (socketing protection).
    * **Low Risk / High Cost:** Potentiometers and Switches get a zero buffer.

---

## 🔬 Tech Stack

- **Python 3.11+** - Core language
- **Regex** - Pattern matching engine for component extraction
- **Pandas** - Data manipulation and aggregation
- **Streamlit** - Interactive web interface
- **CSV/Markdown** - Structured output formats

---

## 📋 Example: Raw BOM → Clean Output

**Input (messy text):**
```text
R1    100k
C1 10uF
R2      47k  1/4W
IC1     TL072
```

**Output ([master_shopping_list.csv](examples/master_shopping_list.csv)):**

| Component | Value | Qty | Buy Qty | Notes |
|-----------|-------|-----|---------|-------|
| R1        | 100kΩ | 1   | 10      | Buffer: +5 (Minimum 10) |
| R2        | 47kΩ  | 1   | 10      | Buffer: +5 (Minimum 10) |
| C1        | 10µF  | 1   | 4       | Buffer: +3 |
| IC1       | TL072 | 1   | 2       | Buffer: +1 (Backup) |
| Socket    | DIP-8 | 1   | 2       | Auto-injected for IC1 |

---

## 📦 Project Structure
```text
pedal-bom-manager/
├── .gitignore
├── app.py                 <-- Interface: Streamlit Web App
├── cli.py                 <-- Interface: Command Line Tool
├── assets/
│   └── demo.gif           <-- Demo: Visual walkthrough
├── data/                  <-- Input: Sample BOM files
│   ├── big_muff.txt
│   ├── bluesbreaker.txt
│   ├── dr_q.txt
│   └── rat.txt
├── examples/              <-- Output: Sample generated files
│   ├── master_shopping_list.csv
│   └── shopping_checklist.md
├── src/
│   └── bom_lib.py         <-- Logic: Regex engine, verification, and buying rules
├── requirements.txt       <-- Dependencies
├── LICENSE                <-- MIT License
└── README.md
```

**Key Files:**
- **[app.py](app.py)** - Streamlit web interface
- **[cli.py](cli.py)** - Command-line batch processor
- **[src/bom_lib.py](src/bom_lib.py)** - Core parsing and verification logic
- **[examples/master_shopping_list.csv](examples/master_shopping_list.csv)** - Sample output (CSV)
- **[examples/shopping_checklist.md](examples/shopping_checklist.md)** - Sample output (Markdown)

---

## 💻 Usage

### Option 1: The Web Interface (Live App)

**🌐 [Use the hosted app here](https://pedal-bom-manager.streamlit.app/)** - No installation required!

Simply paste your BOM text and download your shopping list.

### Option 2: Run Locally (Streamlit)

To run the web interface on your own machine:

1.  Install dependencies:
```bash
    pip install -r requirements.txt
```
2.  Launch the app:
```bash
    streamlit run app.py
```
3.  Paste your BOM text into the window and download your CSV.

### Option 3: The Command Line Tool (CLI)

For batch processing local files:

1.  Place your text files (e.g., `big_muff.txt`) inside the `/data` folder.
2.  Run the script:
```bash
    python cli.py
```
3.  Check the terminal for the Verification Report and find your generated files in the working directory.

---

## 📊 Sample Output (Verification Report)

When running the CLI, the tool provides a detailed report on the integrity of the parsing process:
```text
📂 Found 4 BOM files in 'data':
   - Loaded: big_muff.txt
   - Loaded: bluesbreaker.txt
   - Loaded: dr_q.txt
   - Loaded: rat.txt

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

✅ CSV saved: master_shopping_list.csv
✅ Markdown saved: shopping_checklist.md
```

---

## 📝 Generated Artifacts

The tool produces two files:

1.  **[master_shopping_list.csv](examples/master_shopping_list.csv)**: A clean spreadsheet sorted by component priority (PCBs -> ICs -> Passives). Includes a "Notes" column with auto-generated warnings.
2.  **[shopping_checklist.md](examples/shopping_checklist.md)**: A GitHub-ready markdown table with checkboxes for tracking your order status.

Sample outputs can be found in the `/examples` directory.

---

## 🔧 Installation & Setup

**Prerequisites:** Python 3.10+
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/pedal-bom-manager.git

# 2. Navigate to the project directory
cd pedal-bom-manager

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## 🤝 Contributing

Found a bug? Have an idea for improvement? Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

**Jackson Ferguson**

- **GitHub:** [@JacksonFergusonDev](https://github.com/JacksonFergusonDev)
- **LinkedIn:** [Jackson Ferguson](https://www.linkedin.com/in/jackson--ferguson/)
- **Email:** jackson.ferguson0@gmail.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.