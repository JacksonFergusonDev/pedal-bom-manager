import streamlit as st
import csv
import io
from src.bom_lib import parse_with_verification, get_buy_details, get_residual_report, get_injection_warnings, sort_inventory

st.set_page_config(page_title="Pedal BOM Manager", page_icon="🎸")

st.title("🎸 Guitar Pedal BOM Manager")
st.markdown("""
**Automate your electronics shopping list.**

Paste your raw component lists from DIY pedal projects below. 
This tool will combine them, clean them using Regex, and apply **Nerd Economics** (automatic buffers for cheap parts) to generate a Master Shopping List.
""")

# Input Area
raw_input = st.text_area("Paste BOM Text Here (You can paste multiple pedals one after another):", height=300)

if st.button("Generate Shopping List", type="primary"):
    if not raw_input:
        st.error("Please paste some text first!")
    else:
        # 1. Processing
        master_list, statistics = parse_with_verification([raw_input])
        
        # 2. Display Reports
        st.subheader("📊 Verification Report")
        col1, col2 = st.columns(2)
        col1.metric("Lines Scanned", statistics['lines_read'])
        col2.metric("Parts Extracted", statistics['parts_found'])
        
        # Residual Analysis
        suspicious = get_residual_report(statistics)
        if suspicious:
            st.warning(f"⚠️ Found {len(suspicious)} suspicious lines that were skipped:")
            for line in suspicious:
                st.code(line)
        else:
            st.success("✅ Clean Parse: No suspicious missed lines.")
            
        # Logic Injections
        warnings = get_injection_warnings(master_list)
        if warnings:
            st.info("💡 Logic Assumptions Made:")
            for w in warnings:
                st.write(w)

        # 3. Data Prep
        prepared_data = []
        
        # OLD: sorted_parts = sorted(master_list.items(), key=lambda x: x[0])
        # NEW: Use the smart sorter
        sorted_parts = sort_inventory(master_list)
        
        for part_key, count in sorted_parts:
            if " | " not in part_key: continue
            category, value = part_key.split(" | ", 1)
            buy_qty, note = get_buy_details(category, value, count)
            prepared_data.append({
                "Category": category, "Part": value, "BOM Qty": count, "Buy Qty": buy_qty, "Notes": note
            })
            
        # 4. Show Data Table
        st.subheader("🛒 Master Shopping List")
        st.dataframe(prepared_data, use_container_width=True)
        
        # 5. Download Buttons
        # Create CSV String
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=["Category", "Part", "BOM Qty", "Buy Qty", "Notes"])
        writer.writeheader()
        writer.writerows(prepared_data)
        csv_str = csv_buffer.getvalue()
        
        # Create Markdown String
        md_str = "# Master Pedal Shopping List\n\n| Category | Part | BOM Qty | Buy Qty | Notes |\n|---|---|---|---|---|\n"
        for row in prepared_data:
            md_str += f"| {row['Category']} | **{row['Part']}** | {row['BOM Qty']} | **{row['Buy Qty']}** | *{row['Notes']}* |\n"

        col_d1, col_d2 = st.columns(2)
        
        col_d1.download_button(
            label="Download as CSV (Excel)",
            data=csv_str,
            file_name="shopping_list.csv",
            mime="text/csv"
        )
        
        col_d2.download_button(
            label="Download as Checklist (Markdown)",
            data=md_str,
            file_name="checklist.md",
            mime="text/markdown"
        )