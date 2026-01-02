# Dictionary of pre-defined BOMs.
# You can copy-paste raw text from PedalPCB PDFs or Tayda project pages here.
BOM_PRESETS = {
    "PedalPCB: Parentheses Fuzz (Life Pedal)": """
    R1 1M
    R2 1M
    R3 100k
    C1 100n
    C2 100n
    Q1 2N5088
    Q2 2N5088
    D1 1N4148
    D2 1N4148
    IC1 LM308
    POT1 100k-A Volume
    POT2 100k-B Distortion
    POT3 100k-C Filter
    """,
    "Classic: Tube Screamer (TS808)": """
    R1 1k
    R2 510k
    R3 10k
    C1 20n
    C2 1u
    IC1 JRC4558D
    D1 1N914
    D2 1N914
    Q1 2N3904
    Q2 2N3904
    DRIVE 500k-A
    TONE 20k-W
    LEVEL 100k-B
    """,
    "Fuzz Face (Silicon)": """
    Q1 BC108
    Q2 BC108
    R1 33k
    R2 330
    R3 8k2
    R4 100k
    C1 2.2u
    C2 10n
    C3 47u
    VOL B500k
    FUZZ B1k
    """,
}
