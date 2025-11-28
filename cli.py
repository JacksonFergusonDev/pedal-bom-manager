import os
import csv
import sys
from src.bom_lib import parse_with_verification, get_buy_details, get_residual_report, get_injection_warnings, sort_inventory

def load_boms_from_folder(folder_path="data"):
    loaded_boms = []
    
    if not os.path.exists(folder_path):
        print(f"❌ ERROR: Folder '{folder_path}' not found.")
        print(f"   >> Create a folder named '{folder_path}' and put your .txt files in it.")
        sys.exit()

    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    
    if not files:
        print(f"⚠️  WARNING: No .txt files found in '{folder_path}'.")
        sys.exit()

    print(f"📂 Found {len(files)} BOM files in '{folder_path}':")
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                loaded_boms.append(content)
                print(f"   - Loaded: {filename}")
        except Exception as e:
            print(f"   ❌ Failed to read {filename}: {e}")
            
    return loaded_boms

if __name__ == "__main__":
    print("\n--- Starting Execution ---")
    
    # 1. Load Data
    all_boms = load_boms_from_folder("data")
    
    # 2. Parse Data
    master_list, stats = parse_with_verification(all_boms)
    
    # 3. Verification Report
    print("\n" + "="*40)
    print("VERIFICATION REPORT (RESIDUAL ANALYSIS)")
    print("="*40)
    print(f"Total Lines Scanned: {stats['lines_read']}")
    print(f"Parts Extracted:     {stats['parts_found']}")
    print("-" * 40)
    
    suspicious_lines = get_residual_report(stats)
    
    if len(suspicious_lines) == 0:
        print("✅ SUCCESS: Residuals look like pure noise. No missed parts detected.")
    else:
        print(f"⚠️  WARNING: Found {len(suspicious_lines)} suspicious lines that were NOT parsed!")
        print("Check these manually to ensure they aren't missing parts:\n")
        for bad_line in suspicious_lines:
            print(f"   >> {bad_line}")
    print("="*40 + "\n")
    
    # 4. Injection Report
    print("LOGIC INJECTION REPORT (Assumptions Made)")
    print("="*40)
    warnings = get_injection_warnings(master_list)
    
    if not warnings:
        print("✅ No logic injections detected.")
    else:
        for w in warnings:
            print(w)
    print("="*40 + "\n")
    
    # 5. Data Preparation
    prepared_data = []
    
    # OLD: sorted_parts = sorted(master_list.items(), key=lambda x: x[0])
    # NEW: Use the smart sorter
    sorted_parts = sort_inventory(master_list)

    for part_key, count in sorted_parts:
        if " | " not in part_key: continue
        category, value = part_key.split(" | ", 1)
        
        buy_qty, note = get_buy_details(category, value, count)
        
        prepared_data.append({
            "Category": category, 
            "Part": value, 
            "BOM_Qty": count, 
            "Buy_Qty": buy_qty, 
            "Notes": note
        })

    # --- NEW OUTPUT LOGIC ---
    
    # Define the directory
    output_dir = "output"
    
    # Create it if it doesn't exist (mkdir -p)
    os.makedirs(output_dir, exist_ok=True)
    
    # Define full paths
    csv_path = os.path.join(output_dir, "master_shopping_list.csv")
    md_path = os.path.join(output_dir, "shopping_checklist.md")

    # 6. Write CSV
    try:
        with open(csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Part Value", "BOM Qty", "Buy Qty", "Notes"])
            for row in prepared_data:
                writer.writerow([row["Category"], row["Part"], row["BOM_Qty"], row["Buy_Qty"], row["Notes"]])
        print(f"✅ CSV saved: {csv_path}")
    except PermissionError:
        print(f"❌ ERROR: Close {csv_path}!")

    # 7. Write Markdown
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Master Pedal Shopping List\n\n")
            f.write("| Category | Part Value | BOM Qty | Buy Qty | Notes |\n")
            f.write("| --- | --- | :---: | :---: | --- |\n")
            for row in prepared_data:
                f.write(f"| {row['Category']} | **{row['Part']}** | {row['BOM_Qty']} | **{row['Buy_Qty']}** | *{row['Notes']}* |\n")
        print(f"✅ Markdown saved: {md_path}")
    except PermissionError:
        print(f"❌ ERROR: Close {md_path}!")

    print("--- Done! ---")