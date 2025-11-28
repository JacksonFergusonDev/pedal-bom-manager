import re
from collections import defaultdict

def parse_with_verification(bom_list):
    """
    Parses a list of raw BOM strings.
    Returns:
        master_inventory: defaultdict(int) of parts
        stats: dict containing metrics and residual lines
    """
    master_inventory = defaultdict(int)
    
    stats = {
        "lines_read": 0,
        "parts_found": 0,
        "residuals": [] 
    }

    pattern = re.compile(r"^([a-zA-Z0-9_]+)\s+([0-9a-zA-Z\.\-\/]+).*")
    
    # Valid prefixes
    valid_prefixes = ('R', 'C', 'D', 'Q', 'U', 'IC', 'SW', 'POT', 'TRIM', 'VOL', 'TONE', 'GAIN', 'SUSTAIN', 'SENS', 'RANGE', 'OP', 'TL')

    for raw_text in bom_list:
        lines = raw_text.strip().split('\n')
        capture_next_line_as_pcb = False
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            stats["lines_read"] += 1
            
            # --- PCB TRAP START ---
            if line.upper() == "PCB":
                capture_next_line_as_pcb = True
                continue 
            
            if capture_next_line_as_pcb:
                # CLEANUP LOGIC: Remove redundant "PCB" prefix if present
                clean_name = re.sub(r'^PCB\s+', '', line, flags=re.IGNORECASE).strip()
                
                master_inventory[f"PCB | {clean_name}"] += 1
                stats["parts_found"] += 1
                capture_next_line_as_pcb = False
                continue
            # --- PCB TRAP END ---

            # --- REGEX MATCH ---
            match = pattern.match(line)
            parsed_successfully = False
            
            if match:
                ref = match.group(1).upper()
                val = match.group(2).upper()

                is_valid_prefix = any(ref.startswith(p) for p in valid_prefixes)
                
                # Special check for Pot names
                if 'POT' in ref or ref in ['VOL', 'TONE', 'GAIN', 'SUSTAIN', 'SENS', 'RANGE']:
                    is_valid_prefix = True

                if is_valid_prefix:
                    # CATEGORIZATION
                    category = "Unknown"
                    if ref.startswith('R') and not ref.startswith('RANGE'): category = "Resistors"
                    elif ref.startswith('C'): category = "Capacitors"
                    elif ref.startswith('D'): category = "Diodes"
                    elif ref.startswith('Q'): category = "Transistors"
                    elif ref.startswith('SW'): category = "Switches"
                    elif 'POT' in ref or ref in ['VOL', 'TONE', 'GAIN', 'SUSTAIN', 'SENS', 'RANGE']: category = "Potentiometers"
                    
                    # --- IC LOGIC (With Socket Injection) ---
                    elif ref.startswith('U') or ref.startswith('IC') or ref.startswith('OP') or ref.startswith('TL'): 
                        category = "ICs"
                        # INJECTION: If it's a chip, we need a socket.
                        master_inventory[f"Hardware/Misc | 8_PIN_DIP_SOCKET"] += 1

                    # --- SMD INJECTION ---
                    if "2N5457" in val:
                        val = "MMBF5457"
                        master_inventory[f"Hardware/Misc | SMD_ADAPTER_BOARD"] += 1
                    elif "MMBF5457" in val:
                        master_inventory[f"Hardware/Misc | SMD_ADAPTER_BOARD"] += 1
                    
                    master_inventory[f"{category} | {val}"] += 1
                    parsed_successfully = True
                    stats["parts_found"] += 1

            # --- RESIDUAL LOGGING ---
            if not parsed_successfully:
                stats["residuals"].append(line)

    return master_inventory, stats

def get_residual_report(stats):
    """
    Analyzes unparsed lines. Returns a list of 'suspicious' lines that contain numbers but were skipped.
    """
    safe_keywords = ["RESISTORS", "CAPACITORS", "TRANSISTORS", "DIODES", "POTENTIOMETERS", "PCB", "COMPONENT LIST", "EQUIVALENTS", "SOCKET", "OPAMP"]
    
    suspicious_lines = []
    
    for line in stats["residuals"]:
        upper_line = line.upper()
        
        is_safe = False
        for kw in safe_keywords:
            if kw in upper_line:
                is_safe = True
                break
        
        if not is_safe:
            if any(char.isdigit() for char in line):
                suspicious_lines.append(line)
                
    return suspicious_lines

def get_injection_warnings(inventory):
    """
    Checks the inventory for auto-injected items and returns specific warning messages.
    FIXED: Uses .get() to avoid creating 0-count entries in the defaultdict.
    """
    warnings = []
    
    # Check for SMD Adapters
    if inventory.get("Hardware/Misc | SMD_ADAPTER_BOARD", 0) > 0:
        warnings.append("⚠️  SMD ADAPTERS: Script forced adapters for MMBF5457.")
        warnings.append("    >> ACTION: Check if your PCB already has SOT-23 pads. If so, don't buy these.")

    # Check for IC Sockets
    if inventory.get("Hardware/Misc | 8_PIN_DIP_SOCKET", 0) > 0:
        warnings.append("ℹ️  IC SOCKETS: Script forced sockets for all DIP chips.")
        warnings.append("    >> ACTION: Highly recommended, but optional if you prefer direct soldering.")
        
    return warnings

def get_buy_details(category, val, count):
    """
    Applies Nerd Economics to calculate buy quantities and notes.
    """
    buy_qty = count
    note = ""
    
    # CATEGORY RULES
    if category == "Resistors": buy_qty = max(10, count + 5)
    elif category == "Capacitors":
        if "100N" in val or "0.1U" in val: 
            buy_qty = count + 10
            note = "Power filtering (buy bulk)."
        else: buy_qty = count + 3
    elif category == "Diodes": buy_qty = max(10, count + 5)
    elif category == "Transistors":
        if "MMBF" in val: 
            buy_qty = count + 5
            note = "SMD SUB for 2N5457. Solder to Adapter!"
        else: buy_qty = count + 3
    
    # ICs: Socket is explicit, just backup the chip.
    elif category == "ICs": 
        buy_qty = count + 1
        note = "Audio Chip (Socket added below)"
        
    elif category == "Hardware/Misc": 
        if "ADAPTER" in val: 
            buy_qty = count + 4
            # WARN: Explicitly state this was an assumption
            note = "[AUTO-ADDED] Verify if PCB needs adapter or has native SOT-23 pads."
        elif "SOCKET" in val:
            buy_qty = count + 2 
            # WARN: Explicitly state this is for safety
            note = "[AUTO-ADDED] Recommended for chip safety/swapping."
        else: buy_qty = count + 1
        
    elif category == "PCB":
        buy_qty = count 
        note = "Main Board"

    return buy_qty, note

def sort_inventory(inventory):
    """
    Sorts the inventory based on 'Nerd Shopping Priority'.
    """
    priority_order = [
        "PCB",
        "ICs",
        "Transistors",
        "Diodes",
        "Potentiometers",
        "Switches",
        "Hardware/Misc",
        "Capacitors",
        "Resistors"
    ]
    
    priority_map = {name: i for i, name in enumerate(priority_order)}
    
    def sort_key(item):
        full_key = item[0] 
        if " | " not in full_key: 
            return (999, full_key)
        category, value = full_key.split(" | ", 1)
        rank = priority_map.get(category, 100)
        return (rank, value)

    return sorted(inventory.items(), key=sort_key)