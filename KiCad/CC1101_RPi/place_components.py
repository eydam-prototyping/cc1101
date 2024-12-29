import pcbnew

reference_part_mapping = {
  "U1001": ["U2001", "U3001", "U4001"],
  "D1001": ["D2001", "D3001", "D4001"],
  "D1002": ["D2002", "D3002", "D4002"],
  "R1001": ["R2001", "R3001", "R4001"],
  "R1002": ["R2002", "R3002", "R4002"],
  "R1171": ["R2171", "R3171", "R4171"],
  "Q1001": ["Q2001", "Q3001", "Q4001"],
  "Q1002": ["Q2002", "Q3002", "Q4002"],
  "C1001": ["C2001", "C3001", "C4001"],
  "C1002": ["C2002", "C3002", "C4002"],
  "C1003": ["C2003", "C3003", "C4003"],
  "C1004": ["C2004", "C3004", "C4004"],
  "C1005": ["C2005", "C3005", "C4005"],
  "C1006": ["C2006", "C3006", "C4006"],
  "C1051": ["C2051", "C3051", "C4051"],
  "C1081": ["C2081", "C3081", "C4081"],
  "C1101": ["C2101", "C3101", "C4101"],
  "Y1001": ["Y2001", "Y3001", "Y4001"],
  "C1131": ["C2131"],
  "L1121": ["L2121"],
  "L1131": ["L2131"],
  "C1121": ["C2121"],
  "C1124": ["C2124"],
  "L1122": ["L2122"],
  "L1123": ["L2123"],
  "C1122": ["C2122"],
  "C1123": ["C2123"],
  "C1125": ["C2125"],
  "J1001": ["J2001"],
  "L3131": ["L4131"],
  "L3121": ["L4121"],
  "C3121": ["C4121"],
  "L3122": ["L4122"],
  "C3131": ["C4131"],
  "L3132": ["L4132"],
  "C3122": ["C4122"],
  "C3124": ["C4124"],
  "L3123": ["L4123"],
  "C3123": ["C4123"],
  "L3124": ["L4124"],
  "C3126": ["C4126"],
  "C3125": ["C4125"],
  "L3125": ["L4125"],
  "J3001": ["J4001"],
}

parts = {}

board = pcbnew.GetBoard()

for footprint in board.Footprints():
    parts[footprint.GetReference()] = footprint

offset = (0, 20000000)

for reference_part in reference_part_mapping:
    reference_part_footprint = parts[reference_part]
    for i, part in enumerate(reference_part_mapping[reference_part]):
        part_footprint = parts[part]
        part_footprint.SetX(reference_part_footprint.GetPosition().x + (i+1) * offset[0])
        part_footprint.SetY(reference_part_footprint.GetPosition().y + (i+1) * offset[1])
        part_footprint.SetOrientation(reference_part_footprint.GetOrientation())

        for field in part_footprint.GetFields():
            position = field.GetPosition()
            reference_field = reference_part_footprint.GetFieldByName(field.GetName())
            reference_field_position = reference_field.GetPosition()
            #print(f"Part {part}, Field {field.GetName()} at {position.x} -> {reference_field_position.x}, {position.y} -> {reference_field_position.y}")
            field.SetX(reference_field_position.x + (i+1) * offset[0])
            field.SetY(reference_field_position.y + (i+1) * offset[1])
            field.SetAttributes(reference_field.GetAttributes())

#exec(open(r"C:\Projekte\19_mpy_cc1101\KiCad\CC1101_RPi\place_components.py").read())