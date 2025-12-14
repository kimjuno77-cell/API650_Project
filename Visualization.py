import math

def generate_shell_svg(diameter, shell_courses, svg_height=400):
    """
    Generates an SVG string representing the shell course stackup.
    """
    # Dimensions
    total_h = sum(c['Width'] for c in shell_courses)
    if total_h == 0: return ""
    
    scale_y = (svg_height - 40) / total_h
    scale_x = scale_y * 2 # Exaggerate width for visibility? Or Keep proportional?
    # Tanks are wide. If we keep aspect ratio, H is small compared to D usually.
    # Let's use fixed width for drawing course blocks, as thickness is irrelevant to visual width in stackup view.
    # Stackup View: Vertical Rectangles.
    
    svg_width = 300
    rect_width = 150
    start_x = (svg_width - rect_width) / 2
    
    svg = [f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.text { font-family: Arial; font-size: 12px; } .dim { font-size: 10px; fill: gray; }</style>')
    
    current_y = svg_height - 20 # Start from bottom (minus margin)
    
    # Draw Ground Line
    svg.append(f'<line x1="20" y1="{current_y}" x2="{svg_width-20}" y2="{current_y}" stroke="black" stroke-width="2" />')
    
    for i, c in enumerate(shell_courses):
        h_px = c['Width'] * scale_y
        
        # Course Rect
        svg.append(f'<rect x="{start_x}" y="{current_y - h_px}" width="{rect_width}" height="{h_px}" fill="#e3f2fd" stroke="#1565c0" stroke-width="1" />')
        
        # Text: Course Name & Thickness
        label = f"{c['Course']}"
        detail = f"t={c['t_used']}mm"
        
        text_y = current_y - (h_px / 2) + 4
        svg.append(f'<text x="{start_x + rect_width/2}" y="{text_y}" text-anchor="middle" class="text" fill="black">{label}</text>')
        svg.append(f'<text x="{start_x + rect_width + 10}" y="{text_y}" text-anchor="start" class="dim">{detail}</text>')
        
        # Height Dim
        svg.append(f'<text x="{start_x - 10}" y="{text_y}" text-anchor="end" class="dim">H={c["Width"]:.3f}m</text>')
        
        current_y -= h_px
        
    # Title
    svg.append(f'<text x="{svg_width/2}" y="20" text-anchor="middle" font-weight="bold" class="text">Shell Course Stackup</text>')
    
    svg.append('</svg>')
    return "".join(svg)

def generate_nozzle_orientation_svg(diameter, nozzles, svg_size=400):
    """
    Generates an SVG string representing nozzle orientation (Top View).
    """
    cx = svg_size / 2
    cy = svg_size / 2
    radius = (svg_size - 60) / 2
    
    svg = [f'<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.mark { font-family: Arial; font-size: 11px; font-weight: bold; } .angle { font-size: 9px; fill: gray; }</style>')
    
    # Tank Circle
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="black" stroke-width="2" />')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="2" fill="black" />') # Center
    
    # 0, 90, 180, 270 Markers
    # 0 is usually North or East? API 650 doesn't specify. Usually North=0 or East=0. 
    # Let's assume standard math notation (East 0) or Compass (North 0)?
    # Plant layouts usually have North (0 or 90). Let's assume North is UP (0 deg).
    # SVG y is down. So 0 deg = (cx, cy-r).
    
    # Draw Nozzles
    for n in nozzles:
        deg = n.get('Orientation', 0)
        mark = n.get('Mark', '?')
        size = n.get('Size', '?')
        
        # Convert deg to rad (0 deg = North/Up, Clockwise)
        # Math: 0 is Right. 
        # Engineering: 0 is North (Up). Clockwise.
        # Rad = (deg - 90) * pi / 180 ? 
        # let's calculate pos based on 0=Up, CW.
        rad = (deg - 90) * math.pi / 180.0
        
        # x = cx + r * cos(rad)
        # y = cy + r * sin(rad)
        
        # Adjust for drawing text outside
        text_r = radius + 20
        line_r = radius
        
        x_line = cx + line_r * math.cos(rad)
        y_line = cy + line_r * math.sin(rad)
        
        x_text = cx + (text_r + 5) * math.cos(rad)
        y_text = cy + (text_r + 5) * math.sin(rad)
        
        # Nozzle Line
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x_line}" y2="{y_line}" stroke="red" stroke-width="1" stroke-dasharray="4" />')
        
        # Nozzle Point
        svg.append(f'<circle cx="{x_line}" cy="{y_line}" r="4" fill="red" />')
        
        # Label
        # Adjust alignment based on quadrant
        anchor = "middle"
        baseline = "middle"
        # Not perfect but sufficient
        
        svg.append(f'<text x="{x_text}" y="{y_text}" text-anchor="{anchor}" class="mark">{mark} ({deg}°)</text>')
        
    svg.append(f'<text x="{cx}" y="{svg_size-10}" text-anchor="middle" class="text" font-weight="bold">Nozzle Orientation (0° North, CW)</text>')
    svg.append('</svg>')
    return "".join(svg)

def generate_wind_moment_svg(D, H, P_wind_kPa, M_wind_kNm):
    """
    Generates SVG showing Wind Pressure and Overturning Moment.
    """
    w = 400
    h = 400
    # Margins
    mx, my = 50, 50
    draw_w = w - 2*mx
    draw_h = h - 2*my
    
    # Scale
    # Layout: Tank on Left, Pressure on Right?
    # Or Tank Center, Pressure Arrows hitting it.
    
    # Tank Rect relative dimensions
    # H/D ratio visual
    ratio = H / D if D > 0 else 1
    # Limit visual ratio to avoid extreme skinny/flat
    vis_ratio = max(0.5, min(2.0, ratio))
    
    tank_w_px = 100
    tank_h_px = tank_w_px * vis_ratio
    
    start_x = mx + 100
    base_y = h - my
    top_y = base_y - tank_h_px
    
    svg = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.lbl { font-family: Arial; font-size: 12px; } .dim { font-size: 10px; fill: gray; }</style>')
    
    # Ground
    svg.append(f'<line x1="{mx}" y1="{base_y}" x2="{w-mx}" y2="{base_y}" stroke="black" stroke-width="2" />')
    
    # Tank Rect
    svg.append(f'<rect x="{start_x}" y="{top_y}" width="{tank_w_px}" height="{tank_h_px}" fill="#eeeeee" stroke="black" stroke-width="2" />')
    svg.append(f'<text x="{start_x + tank_w_px/2}" y="{top_y + tank_h_px/2}" text-anchor="middle" class="lbl">Tank</text>')
    
    # Wind Pressure Arrows (from Left)
    num_arrows = 5
    arrow_len = 40
    for i in range(num_arrows):
        ay = top_y + (i + 0.5) * (tank_h_px / num_arrows)
        ax_start = start_x - 10 - arrow_len
        ax_end = start_x - 10
        
        # Arrow Line
        svg.append(f'<line x1="{ax_start}" y1="{ay}" x2="{ax_end}" y2="{ay}" stroke="blue" stroke-width="2" />')
        # Arrow Head
        svg.append(f'<polygon points="{ax_end},{ay} {ax_end-5},{ay-3} {ax_end-5},{ay+3}" fill="blue" />')
        
    svg.append(f'<text x="{start_x - 30}" y="{top_y - 10}" text-anchor="end" class="lbl" fill="blue">Wind Pressure ({P_wind_kPa:.2f} kPa)</text>')
    
    # Moment Arrow (Curved at bottom right)
    # Center of rotation is usually toe? Or center? OTM is calc about base.
    # Draw arc at bottom
    arc_cx = start_x + tank_w_px/2
    arc_cy = base_y
    r_arc = 40
    
    # Path for arc (semi-circleish)
    # M_wind overturning -> Tries to tip tank. Wind from left -> Tips about Right Toe (Downwind).
    # Arrow represents the Moment magnitude.
    # Visualize moment direction: Clockwise (Wind L->R)
    
    # Arc from top-right of center to bottom-right?
    p_start_x = arc_cx
    p_start_y = arc_cy - r_arc
    p_end_x = arc_cx + r_arc
    p_end_y = arc_cy
    
    svg.append(f'<path d="M {arc_cx - 20} {arc_cy - 10} Q {arc_cx} {arc_cy - 50} {arc_cx + 40} {arc_cy - 10}" stroke="red" stroke-width="3" fill="none" marker-end="url(#arrowhead)" />')
    
    # Def Marker
    svg.append('<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="red" /></marker></defs>')
    
    svg.append(f'<text x="{arc_cx + 50}" y="{arc_cy - 20}" class="lbl" fill="red" font-weight="bold">Mw = {M_wind_kNm:.0f} kNm</text>')
    
    svg.append('</svg>')
    return "".join(svg)

def generate_roof_detail_svg(detail_type, angle_size, t_shell_top, t_roof, svg_w=300, svg_h=300):
    """
    Generates SVG for Roof-to-Shell Detail (e.g., Fig F-2).
    """
    cx, cy = 100, 200
    scale = 5.0 # pixels per mm? Sections are small (e.g. 100mm angle).
    
    # L75x75x6 -> 75mm * 5 = 375px Too big.
    # Use fixed visualization size approx.
    # visual_size = 100px for 100mm. Scale = 1.
    scale = 1.5
    
    svg = [f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>.lbl { font-family: Arial; font-size: 12px; } </style>')
    
    # Shell Wall (Vertical)
    # t_shell ~ 6mm. Draw as 10px approx.
    sh_w = max(10, t_shell_top * scale)
    sh_h = 150
    
    # Shell Rect
    svg.append(f'<rect x="{cx}" y="{cy}" width="{sh_w}" height="{sh_h}" fill="#90caf9" stroke="black" />')
    svg.append(f'<text x="{cx - 10}" y="{cy + 50}" text-anchor="end" class="lbl">Shell (t={t_shell_top})</text>')
    
    # Detail Logic
    if "Angle" in detail_type:
        # Draw Angle on top of shell OUTSIDE? Or Inside?
        # API 650 Top Angle usually outside.
        # Draw L Shape.
        # Parse size "L75x75x6"
        try:
            # L75x75x6
            parts = angle_size.replace('L','').split('x')
            leg_h = float(parts[0])
            leg_w = float(parts[1])
            thk = float(parts[2])
        except:
            leg_h, leg_w, thk = 75, 75, 6
            
        l_h = leg_h * scale
        l_w = leg_w * scale
        l_t = thk * scale
        
        # Position: Heel at top-outer corner of shell?
        # Shell is x=cx to cx+sh_w. Outside is Left (cx) or Right?
        # Assume Right is Inside of tank. Left is Outside.
        # Top Angle usually on top edge, vertical leg down outside? Or horizontal leg out?
        # Detail a (Fig F-2): Angle on top edge.
        
        # Draw L shape polygon
        # Origin: Shell Top Left Corner (cx, cy)
        # Vertical leg down?
        # Let's draw generic "Detail a" representation.
        
        # Angle sitting on top edge
        # Vertical Leg
        svg.append(f'<rect x="{cx - l_t}" y="{cy}" width="{l_t}" height="{l_h}" fill="orange" stroke="black" />')
        # Horizontal Leg (Outward)
        svg.append(f'<rect x="{cx - l_w}" y="{cy}" width="{l_w}" height="{l_t}" fill="orange" stroke="black" />')
        
        svg.append(f'<text x="{cx - l_w}" y="{cy - 10}" class="lbl">Top Angle {angle_size}</text>')
        
        # Roof Plate (Sloped)
        # Starts from Shell Top Inside (cx + sh_w, cy)?
        # Slopes up inwards (Right).
        # Slope 1:16 approx.
        roof_len = 100
        dx = roof_len
        dy = -roof_len * 0.2 # Slope exaggerated
        
        rx = cx + sh_w
        ry = cy
        
        svg.append(f'<line x1="{rx}" y1="{ry}" x2="{rx+dx}" y2="{ry+dy}" stroke="black" stroke-width="3" />')
        svg.append(f'<text x="{rx+dx}" y="{ry+dy}" class="lbl">Roof Plate</text>')
        
    else:
        # Butt / Lap
        svg.append(f'<text x="{cx}" y="{cy-20}" class="lbl">Detail: {detail_type} (Generic)</text>')
        # Draw generic roof line
        rx = cx + sh_w
        ry = cy
        svg.append(f'<line x1="{rx}" y1="{ry}" x2="{rx+100}" y2="{ry-20}" stroke="black" stroke-width="3" />')

    svg.append('</svg>')
    return "".join(svg)
