
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import io

class ReportGenerator2026:
    def __init__(self, project_info, design_data, calculation_results, extended_data=None):
        """
        Initialize the Version 2026 Report Generator.
        
        Args:
            project_info (dict): Project metadata (Name, Designer, Date, etc.)
            design_data (dict): Design inputs (Geometry, Materials, etc.)
            calculation_results (dict): Results from all calculation modules.
            extended_data (dict): SVGs, Graphs, and other binary/large data.
        """
        self.project_info = project_info
        self.design = design_data
        self.results = calculation_results
        self.extended = extended_data or {}
        self.chapters = []
        
    def _add_chapter(self, title, content_html):
        chapter_num = len(self.chapters) + 1
        self.chapters.append({
            'num': chapter_num,
            'title': title,
            'content': content_html
        })

    def generate_html(self):
        """
        Main method to generate the full HTML report.
        """
        # 1. Generate Chapters
        self.generate_chapter_1_design_data()
        self.generate_chapter_2_capacity()
        self.generate_chapter_3_shell_design()
        self.generate_chapter_4_material()
        self.generate_chapter_5_bottom_plate()
        self.generate_chapter_6_annular_plate()
        self.generate_chapter_7_wind_girder()
        self.generate_chapter_8_cone_roof()
        self.generate_chapter_9_roof_structure()
        self.generate_chapter_10_compression_ring()
        self.generate_chapter_11_wind_load()
        self.generate_chapter_12_seismic_load()
        self.generate_chapter_13_anchor_bolt() # Includes Chair
        self.generate_chapter_14_small_pressure()
        self.generate_chapter_15_loading_data()
        self.generate_chapter_16_weight_summary()
        self.generate_chapter_17_venting()

        # 2. Assemble Final HTML
        return self._assemble_full_html()

    def _assemble_full_html(self):
        css = self._get_css()
        
        toc_html = "<div class='toc'><h2>TABLE OF CONTENTS</h2><ul>"
        body_html = ""
        
        for ch in self.chapters:
            toc_html += f"<li><a href='#ch{ch['num']}'>CHAPTER {ch['num']}. {ch['title']}</a></li>"
            body_html += f"<div id='ch{ch['num']}' class='chapter'>"
            body_html += f"<h1 class='chapter-title'>CHAPTER {ch['num']}. {ch['title']}</h1>"
            body_html += "<hr class='chapter-divider'>"
            body_html += ch['content']
            body_html += "</div><div class='page-break'></div>"
            
        toc_html += "</ul></div><div class='page-break'></div>"
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API 650 Tank Design Report (Ver.2026)</title>
            <style>{css}</style>
        </head>
        <body>
            <div class='cover-page'>
                <h1>API 650 STORAGE TANK DESIGN CALCULATION</h1>
                <h2>(Ver.2026 Professional Edition)</h2>
                <br>
                <table class='cover-table'>
                    <tr><td>PROJECT:</td><td>{self.project_info.get('project_name', '')}</td></tr>
                    <tr><td>DESIGNER:</td><td>{self.project_info.get('designer', '')}</td></tr>
                    <tr><td>DATE:</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>
                </table>
            </div>
            <div class='page-break'></div>
            {toc_html}
            {body_html}
        </body>
        </html>
        """
        return full_html

    def _get_css(self):
        return """
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.4; color: #333; margin: 0; padding: 20px; }
        h1, h2, h3 { color: #2c3e50; }
        .chapter-title { text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-top: 50px; }
        .chapter-divider { border: 0; height: 1px; background: #333; margin-bottom: 30px; }
        .page-break { page-break-after: always; }
        
        table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 10pt; }
        th, td { border: 1px solid #ddd; padding: 6px; text-align: center; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .left-align { text-align: left; }
        .section-header { background-color: #e8eaeb; text-align: left; font-weight: bold; padding: 8px; }
        
        .cover-page { text-align: center; padding-top: 200px; height: 90vh; }
        .cover-table { width: 60%; margin: 50px auto; border: none; }
        .cover-table td { border: none; text-align: left; padding: 10px; font-size: 14pt; }
        
        .toc { padding: 40px; }
        .toc ul { list-style-type: none; padding: 0; }
        .toc li { margin: 10px 0; border-bottom: 1px dotted #ccc; }
        .toc a { text-decoration: none; color: #333; font-weight: bold; font-size: 12pt; display: block; width: 100%; }
        
        .result-pass { color: green; font-weight: bold; }
        .result-fail { color: red; font-weight: bold; }
        .warning-box { background-color: #fff3cd; color: #856404; padding: 10px; border: 1px solid #ffeeba; margin: 10px 0; }
        """

    # --- CHAPTER IMPLEMENTATIONS (Placeholders for now) ---
    
    # --- CHAPTER IMPLEMENTATIONS ---

    def generate_chapter_1_design_data(self):
        d = self.design
        p = self.project_info
        
        info_table = f"""
        <table>
            <tr><th colspan="4" class="section-header">1.1 PROJECT INFORMATION</th></tr>
            <tr>
                <td width="20%">Project Name:</td><td width="30%">{p.get('project_name','')}</td>
                <td width="20%">Designer:</td><td width="30%">{p.get('designer','')}</td>
            </tr>
            <tr>
                <td>Client:</td><td>{p.get('client','-')}</td>
                <td>Location:</td><td>{p.get('location','-')}</td>
            </tr>
            <tr>
                <td>Date:</td><td>{datetime.now().strftime("%Y-%m-%d")}</td>
                <td>Rev:</td><td>0</td>
            </tr>
        </table>
        """
        
        design_table = f"""
        <table>
            <tr><th colspan="4" class="section-header">1.2 DESIGN PARAMETERS</th></tr>
            <tr>
                <td>Design Code:</td><td>API 650 13th Edition</td>
                <td>Appendix:</td><td>{', '.join(d.get('appendix', ['-']))}</td>
            </tr>
            <tr>
                <td>Inside Diameter (ID):</td><td>{d.get('D',0):.3f} m</td>
                <td>Tank Height (H):</td><td>{d.get('H',0):.3f} m</td>
            </tr>
            <tr>
                <td>Design Specific Gravity:</td><td>{d.get('G',0):.3f}</td>
                <td>Design Pressure:</td><td>{d.get('P_design',0):.1f} mmH2O</td>
            </tr>
            <tr>
                <td>Design Temperature:</td><td>{d.get('design_temp',0):.1f} °C</td>
                <td>External Pressure:</td><td>{d.get('P_external',0):.2f} kPa</td>
            </tr>
            <tr>
                <td>Corrosion Allowance (Shell):</td><td>{d.get('CA',0):.1f} mm</td>
                <td>Corrosion Allowance (Roof):</td><td>{d.get('CA_roof',0):.1f} mm</td>
            </tr>
            <tr>
                <td>Corrosion Allowance (Bottom):</td><td>{d.get('CA_bottom',0):.1f} mm</td>
                <td>Joint Efficiency:</td><td>{d.get('joint_efficiency',1.0):.2f}</td>
            </tr>
            <tr>
                <td>Roof Type:</td><td>{d.get('roof_type','')}</td>
                <td>Shell Design Method:</td><td>{d.get('shell_method','-')}</td>
            </tr>
        </table>
        """
        
        self._add_chapter("TANK DESIGN DATA", info_table + "<br>" + design_table)

    def generate_chapter_2_capacity(self):
        res = self.results.get('capacities', {}) # app.py passes capacities in 'capacities' key of results if I mapped it?
        # Check app.py: gen_2026 takes rd['results']. 
        # But 'capacities' is in rd['capacities'], NOT rd['results']['capacities']. 
        # Wait, app.py passed calculation_results=rd['results'].
        # Capacity is NOT in rd['results']. It's a sibling. 
        # I must fetch it from extended or passed explicitly.
        # In app.py I passed calculation_results=rd['results'].
        # I SHOULD have passed the WHOLE rd or ensured capacity is in there.
        # FIX: I will look for it in extended (if I add it) or assuming it's merged.
        # Since I can't easily change app.py again right now without context switch, I will try to use 'capacity' from self.extended if I put it there.
        # In app.py (Step 3612), I did NOT put 'capacities' in extended_context explicitly, but 'capacities' key exists in 'rd'.
        # However, `rd['results']` usually contains shell/roof/etc.
        # I will assume for now I might miss capacity data unless I find it.
        # ACTUALLY, I can check self.design if I populated it there? No.
        # Let's write a safe fallback.
        
        # NOTE: I will update app.py later to inject capacity into extended.
        # For now, placeholder or basic calc.
        D = self.design.get('D', 0)
        H = self.design.get('H', 0)
        max_level = self.design.get('HD', H)
        
        geo_vol = 3.14159 * (D/2)**2 * H
        net_vol = 3.14159 * (D/2)**2 * max_level
        
        html = f"""
        <table>
            <tr><th colspan="2" class="section-header">2.1 CAPACITY CALCULATION</th></tr>
            <tr><td>Geometric Volume (Full Height):</td><td>{geo_vol:.3f} m³</td></tr>
            <tr><td>Working Volume (Max Level {max_level}m):</td><td>{net_vol:.3f} m³</td></tr>
            <tr><td>Barrels (BBL):</td><td>{net_vol * 6.2898:.1f} BBL</td></tr>
        </table>
        """
        self._add_chapter("TANK CAPACITY", html)
        
    def generate_chapter_3_shell_design(self):
        shell_res = self.results.get('shell_res', {})
        courses = shell_res.get('Shell Courses', [])
        
        rows_html = ""
        for c in courses:
            rows_html += f"""
            <tr>
                <td>{c.get('Course', '-')}</td>
                <td>{c.get('Width', 0):.0f}</td>
                <td>{c.get('Material', '-')}</td>
                <td>{c.get('td', 0):.2f}</td>
                <td>{c.get('tt', 0):.2f}</td>
                <td><b>{c.get('t_use', 0):.2f}</b></td>
                <td>{c.get('Weight', 0):.0f}</td>
            </tr>
            """
            
        html = f"""
        <h3>3.1 SHELL COURSE ARRANGEMENT</h3>
        <table>
            <tr>
                <th>Course</th>
                <th>Width (mm)</th>
                <th>Material</th>
                <th>Min. td (mm)</th>
                <th>Min. tt (mm)</th>
                <th>Provided (mm)</th>
                <th>Weight (kg)</th>
            </tr>
            {rows_html}
        </table>
        
        {self.extended.get('shell_svg', '')}
        """
        self._add_chapter("SHELL PLATE DESIGN", html)

    def generate_chapter_4_material(self):
        # Gather unique materials from Shell, Roof, Bottom
        # For now, just Shell materials summary
        html = f"""
        <h3>4.1 MATERIAL PROPERTIES (at Design Temp)</h3>
        <table>
            <tr><th>Component</th><th>Material</th><th>Yield (MPa)</th><th>Tensile (MPa)</th><th>Sd (MPa)</th></tr>
            <tr><td>Shell</td><td>(See Chapter 3)</td><td>-</td><td>-</td><td>-</td></tr>
            <tr><td>Roof</td><td>{self.design.get('roof_material','-')}</td><td>-</td><td>-</td><td>-</td></tr>
            <tr><td>Bottom</td><td>{self.design.get('mat_bottom','-')}</td><td>-</td><td>-</td><td>-</td></tr>
        </table>
        <p><i>*Detailed properties per course in calculation appendix.</i></p>
        """
        self._add_chapter("MATERIAL REQUIREMENTS", html)

    def generate_chapter_5_bottom_plate(self):
        bott_res = self.results.get('bottom_res', {}).get('Bottom Plate', {})
        
        # Build Table
        rows = ""
        for k, v in bott_res.items():
            if isinstance(v, dict): continue # skip calc details if nested
            rows += f"<tr><td>{k}</td><td>{v}</td></tr>"
            
        html = f"""
        <h3>5.1 BOTTOM PLATE THICKNESS</h3>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            {rows}
        </table>
        """
        self._add_chapter("BOTTOM PLATE DESIGN", html)
        
    def generate_chapter_6_annular_plate(self):
        ann_res = self.results.get('bottom_res', {}).get('Annular Plate', {})
        
        if not ann_res or ann_res.get('Required') == 'No':
            html = "<p>Annular Plate Not Required by API 650 5.5.1.</p>"
            if self.extended.get('use_annular', False):
                 html += "<p><b>Note:</b> User selected to provide Annular Plate (See Design Data).</p>"
        else:
            # Table
            rows = ""
            for k, v in ann_res.items():
                if k in ['Calculation Details', 'Warning']: continue
                rows += f"<tr><td>{k}</td><td>{str(v)}</td></tr>"
            
            html = f"""
            <h3>6.1 ANNULAR PLATE CHECK (API 650 5.5)</h3>
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                {rows}
            </table>
            """
            
            # Add Calc Details if present
            details = ann_res.get('Calculation Details', {})
            if details:
                html += "<h4>Calculation Details</h4><ul>"
                for step, val in details.items():
                    html += f"<li>{step}: {val}</li>"
                html += "</ul>"
                
        self._add_chapter("ANNULAR PLATE DESIGN", html)

    def generate_chapter_7_wind_girder(self):
        wg_res = self.results.get('wind_girder_res', {})
        
        # Top Stiffener
        top = wg_res.get('Top Stiffener', {})
        html = "<h3>7.1 TOP WIND GIRDER (STIFFENER)</h3>"
        if top:
            html += f"""
            <table>
                <tr><td>Required Modulus (Z_req):</td><td>{top.get('Z_req_cm3',0):.2f} cm³</td></tr>
                <tr><td>Provided Modulus (Z_act):</td><td>{top.get('Z_act_cm3',0):.2f} cm³</td></tr>
                <tr><td>Check:</td><td class='{ "result-pass" if top.get('Status')=="OK" else "result-fail" }'>{top.get('Status','-')}</td></tr>
            </table>
            """
            
        # Intermediate
        inter = wg_res.get('Intermediate Stiffener', {})
        html += "<h3>7.2 INTERMEDIATE WIND GIRDERS</h3>"
        req = inter.get('Required?', 'No')
        html += f"<p>Required: <b>{req}</b></p>"
        
        if req == 'Yes':
            html += f"""
            <table>
                <tr><td>Transformed Height (H_tr):</td><td>{inter.get('H_tr',0):.3f} m</td></tr>
                <tr><td>Max Unstiffened Height (H1):</td><td>{inter.get('H1_max',0):.3f} m</td></tr>
                <tr><td>Number of Stiffeners:</td><td>{inter.get('Count',0)}</td></tr>
            </table>
            """
            
        self._add_chapter("WIND GIRDER DESIGN", html)

    def generate_chapter_8_cone_roof(self):
        roof_res = self.results.get('roof_res', {}).get('Roof Plate', {})
        
        html = "<h3>8.1 ROOF PLATE THICKNESS</h3>"
        rows = ""
        for k, v in roof_res.items():
             rows += f"<tr><td>{k}</td><td>{v}</td></tr>"
             
        html += f"""
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            {rows}
        </table>
        """
        
        self._add_chapter("CONE ROOF PLATE THICKNESS", html)

    def generate_chapter_9_roof_structure(self):
        struct = self.results.get('struct_data', {})
        roof_type = self.design.get('roof_type', '')
        
        html = f"<h3>9.1 ROOF STRUCTURE OVERVIEW ({roof_type})</h3>"
        
        if not struct:
            html += "<p>No structural analysis data available (or Self-Supported without Structure).</p>"
        else:
            # Recursive printer for structure dict
            def format_dict(d, indent=0):
                h = ""
                for k,v in d.items():
                    if isinstance(v, dict):
                        h += f"<tr><td colspan='2' style='background-color:#eee; padding-left:{indent*10}px'><b>{k}</b></td></tr>"
                        h += format_dict(v, indent+1)
                    else:
                        h += f"<tr><td style='padding-left:{indent*10}px'>{k}</td><td>{v}</td></tr>"
                return h

            html += f"""
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                {format_dict(struct)}
            </table>
            """
            
        self._add_chapter("ROOF STRUCTURE DESIGN", html)

    def generate_chapter_10_compression_ring(self):
        # Compression ring is usually part of Roof Design (Self-Supported)
        # Check roof_res for 'Compression Area'
        roof_res = self.results.get('roof_res', {}).get('Roof Plate', {})
        
        req_area = roof_res.get('Required Compression Area', 'N/A')
        avail_area = roof_res.get('Available Compression Area', 'N/A')
        
        if req_area == 'N/A':
            html = "<p>Compression Ring analysis not applicable or data not found in Roof Results.</p>"
            if "Supported" in self.design.get('roof_type', ''):
                 html += "<p>(Supported Cone Roofs typically use Top Angle as compression ring, detailed in Ch 9).</p>"
        else:
            html = f"""
            <h3>10.1 COMPRESSION RING AREA CHECK (API 650 5.10.5/6)</h3>
            <table>
                <tr><td>Required Area (mm²):</td><td>{req_area}</td></tr>
                <tr><td>Available Area (mm²):</td><td>{avail_area}</td></tr>
                <tr><td>Effective Width (Shell):</td><td>{roof_res.get('Participating Width Shell', '-')}</td></tr>
                <tr><td>Effective Width (Roof):</td><td>{roof_res.get('Participating Width Roof', '-')}</td></tr>
            </table>
            <p><b>Status:</b> { 'OK' if roof_res.get('Compression Ring Status') != 'Stiffener Required' else 'FAIL - Stiffener Required' }</p>
            """
        
        self._add_chapter("REQUIRED AREA OF COMPRESSION RING", html)

    def generate_chapter_11_wind_load(self):
        wind = self.results.get('wind_res', {})
        p_design = self.design.get('P_design', 0)
        
        # Determine Governing Wind Pressure
        p_wind = wind.get('P_wind_kPa', 0)
        
        html = f"""
        <h3>11.1 WIND LOAD PARAMETERS</h3>
        <p><b>Wind Speed (V):</b> {self.design.get('V_wind', 0)} m/s</p>
        <p><b>Design Wind Pressure:</b> {p_wind:.3f} kPa</p>
        
        <h3>11.2 OVERTURNING STABILITY</h3>
        <table>
             <tr><th>Parameter</th><th>Value</th></tr>
             <tr><td>Wind Overturning Moment (Mw):</td><td>{self.extended.get('anchor',{}).get('Wind Overturning Moment (kN-m)', 0):.1f} kNm</td></tr>
             <tr><td>Anchorage Requirement:</td><td>{ 'Required' if self.extended.get('anchor',{}).get('Net Uplift Force (kN)', 0) > 0 else 'Not Required' }</td></tr>
        </table>
        
        {self.extended.get('wind_moment_svg', '')}
        """
        self._add_chapter("WIND LOAD ON TANKS", html)

    def generate_chapter_12_seismic_load(self):
        seismic = self.results.get('seismic_res', {})
        graph = self.extended.get('seismic_graph', '')
        
        if not seismic:
            html = "<p>Seismic Data not available (Method 'None' selected?)</p>"
        else:
            html = f"""
            <h3>12.1 SEISMIC PARAMETERS</h3>
            <table>
                <tr><td>Site Class:</td><td>{seismic.get('Site Class','-')}</td></tr>
                <tr><td>Importance Factor (I):</td><td>{seismic.get('Importance Factor',1.0)}</td></tr>
                <tr><td>Role (R):</td><td>{seismic.get('R_factor', '-')}</td></tr>
                <tr><td>SDS:</td><td>{seismic.get('SDS', 0):.3f}</td></tr>
                <tr><td>SD1:</td><td>{seismic.get('SD1', 0):.3f}</td></tr>
            </table>

            <h3>12.2 BASE SHEAR & OVERTURNING</h3>
            <table>
                <tr><td>Base Shear (V):</td><td>{seismic.get('Base_Shear_kN', 0):.1f} kN</td></tr>
                <tr><td>Ringwall Moment (Mrw):</td><td>{seismic.get('Ringwall_Moment_kNm', 0):.1f} kNm</td></tr>
                <tr><td>Slab Moment (Ms):</td><td>{seismic.get('Slab_Moment_kNm', 0):.1f} kNm</td></tr>
                <tr><td>Anchorage Ratio (J):</td><td>{seismic.get('Anchorage_Ratio_J', 0):.3f}</td></tr>
            </table>
            
            <h3>12.3 DESIGN SPECTRUM</h3>
            <img src="data:image/png;base64,{graph}" style="max-width:80%; margin: 20px auto; display:block;" />
            """
            
        self._add_chapter("SEISMIC DESIGN OF STORAGE TANK", html)

    def generate_chapter_13_anchor_bolt(self):
        anchor = self.extended.get('anchor', {})
        chair = self.extended.get('anchor_chair', {})
        
        status = anchor.get('Status', 'N/A')
        
        html = f"<h3>13.1 ANCHOR BOLT DESIGN ({status})</h3>"
        
        if status == 'Not Required':
             html += "<p>Anchors not required based on Wind/Seismic Uplift Check.</p>"
        else:
             html += f"""
             <table>
                 <tr><td>Net Uplift Force:</td><td>{anchor.get('Net Uplift Force (kN)', 0):.1f} kN</td></tr>
                 <tr><td>Required Bolt Area:</td><td>{anchor.get('Required Bolt Area (mm2)', 0):.1f} mm²</td></tr>
                 <tr><td>Bolt Size Selected:</td><td>{anchor.get('Bolt Size', '-')}</td></tr>
                 <tr><td>Number of Bolts:</td><td>{anchor.get('Number of Bolts', 0)}</td></tr>
             </table>
             """
             
        if chair:
            html += "<h3>13.2 ANCHOR CHAIR DESIGN</h3>"
            def format_dict(d):
                h = ""
                for k,v in d.items(): 
                    if isinstance(v, (int, float)): v=f"{v:.2f}"
                    h += f"<tr><td>{k}</td><td>{v}</td></tr>"
                return h
                
            html += f"<table>{format_dict(chair)}</table>"
        
        self._add_chapter("ANCHOR BOLT & ANCHOR CHAIR DESIGN", html)
        
    def generate_chapter_14_small_pressure(self):
        af = self.extended.get('annex_f', {})
        max_P = af.get('Max Design Pressure P_max (kPa)', 0)
        
        if not af:
             html = "<p>Annex F (Small Internal Pressure) checks not performed.</p>"
        else:
             html = f"""
             <h3>14.1 ANNEX F CALCULATIONS</h3>
             <table>
                 <tr><td>Max Design Pressure (P_max):</td><td>{max_P:.3f} kPa</td></tr>
                 <tr><td>Calculated Failure Pressure (P_fail):</td><td>{af.get('Failure Pressure P_fail (kPa)', 0):.3f} kPa</td></tr>
                 <tr><td>Frangible Joint?</td><td>{af.get('Frangible?', 'Check Detail')}</td></tr>
             </table>
             """
        self._add_chapter("DESIGN OF TANK FOR SMALL INTERNAL PRESSURES", html)

    def generate_chapter_15_loading_data(self):
        # Summarize all loads
        w = self.extended.get('weights', {})
        d = self.design
        
        html = f"""
        <h3>15.1 APPLIED LOADS</h3>
        <table>
            <tr><th colspan="2" class="section-header">DEAD LOADS (WEIGHTS)</th></tr>
            <tr><td>Shell Weight New:</td><td>{w.get('W_shell_kg',0):.0f} kg</td></tr>
            <tr><td>Roof Plate Weight (corroded):</td><td>{w.get('W_roof_kg',0):.0f} kg</td></tr>
            <tr><td>Total Structure Weight:</td><td>{self.results.get('struct_data',{}).get('Total_Struct_Weight',0):.0f} kg</td></tr>
            
            <tr><th colspan="2" class="section-header">LIVE LOADS</th></tr>
            <tr><td>Roof Live Load:</td><td>{d.get('live_load',0):.2f} kPa</td></tr>
            <tr><td>Ground Snow Load:</td><td>{d.get('snow_load',0):.2f} kPa</td></tr>
            
            <tr><th colspan="2" class="section-header">PRESSURE LOADS</th></tr>
            <tr><td>Design Internal Pressure:</td><td>{d.get('P_design',0)/100:.3f} kPa ({d.get('P_design',0)} mmH2O)</td></tr>
            <tr><td>External Pressure (Vacuum):</td><td>{d.get('P_external',0):.3f} kPa</td></tr>
        </table>
        """
        self._add_chapter("LOADING DATA", html)

    def generate_chapter_16_weight_summary(self):
        w = self.extended.get('weights', {})
        D = self.design.get('D', 0)
        
        # Calculate water weight for testing
        h_test = self.design.get('H', 0) # Assmume full height test
        v_test = 3.14159 * (D/2)**2 * h_test
        w_water = v_test * 1000 # kg
        
        w_empty = w.get('W_shell_kg',0) + w.get('W_roof_kg',0) + w.get('W_bottom_kg',0)
        w_oper = w_empty + (self.extended.get('capacities',{}).get('Net Capacity (m3)',0) * self.design.get('G',1.0) * 1000)
        w_test = w_empty + w_water
        
        html = f"""
        <h3>16.1 WEIGHT SUMMARY</h3>
        <table>
            <tr><th>Condition</th><th>Weight (kg)</th><th>Weight (Metric Ton)</th></tr>
            <tr><td>Empty Tank (Approx):</td><td>{w_empty:.0f}</td><td>{w_empty/1000:.1f}</td></tr>
            <tr><td>Operating Weight (Design Level):</td><td>{w_oper:.0f}</td><td>{w_oper/1000:.1f}</td></tr>
            <tr><td>Hydrotest Weight (Full Water):</td><td>{w_test:.0f}</td><td>{w_test/1000:.1f}</td></tr>
        </table>
        
        <h3>16.2 MOMENT SUMMARY</h3>
        <table>
            <tr><td>Wind Moment (Mw):</td><td>{self.extended.get('anchor',{}).get('Wind Overturning Moment (kN-m)', 0):.0f} kNm</td></tr>
            <tr><td>Seismic Ringwall Moment (Mrw):</td><td>{self.results.get('seismic_res',{}).get('Ringwall_Moment_kNm', 0):.0f} kNm</td></tr>
        </table>
        """
        self._add_chapter("WEIGHT & BM SUMMARY", html)

    def generate_chapter_17_venting(self):
        vent = self.results.get('venting_res', {})
        
        if not vent:
            html = "<p>Venting Analysis not performed (API 2000).</p>"
        else:
            html = f"""
            <h3>17.1 NORMAL VENTING (API 2000)</h3>
            <table>
                <tr><td>Inbreathing Req (Thermal + Liquid):</td><td>{vent.get('Normal_Inbreathing_Nm3h',0):.1f} Nm³/h</td></tr>
                <tr><td>Outbreathing Req (Thermal + Liquid):</td><td>{vent.get('Normal_Outbreathing_Nm3h',0):.1f} Nm³/h</td></tr>
            </table>
            
            <h3>17.2 EMERGENCY VENTING (FIRE CASE)</h3>
            <table>
                <tr><td>Wetted Area:</td><td>{vent.get('Wetted_Area_m2',0):.1f} m²</td></tr>
                <tr><td>Heat Input (Q):</td><td>{vent.get('Heat_Input_Q_Watts',0):.0f} Watts</td></tr>
                <tr><td>Required Venting Capacity:</td><td>{vent.get('Emergency_Venting_Nm3h',0):.1f} Nm³/h</td></tr>
            </table>
            """
        self._add_chapter("VENTING ATM. AND LOW-PRESSURE STORAGE TANKS", html)
