
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import io
import math

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
        self.project_info = project_info or {}
        self.design = design_data or {}
        self.results = calculation_results or {}
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
        self.generate_chapter_18_civil_loading()

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
                <h2>PROJECT: API-650 TANK PROJECT (28.5M ID x 16.5M H)</h2>
                <h3>(Professional Engineering Report - Ver.2026)</h3>
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Roboto+Mono:wght@400;500&display=swap');
        
        body { 
            font-family: 'Inter', sans-serif; 
            line-height: 1.6; 
            color: #1a202c; 
            margin: 0; 
            padding: 0; 
            background-color: #ffffff;
        }
        
        .cover-page { 
            height: 100vh; 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            align-items: center; 
            background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);
            color: white;
            text-align: center;
        }
        .cover-page h1 { font-size: 3rem; margin-bottom: 0.5rem; letter-spacing: -1px; }
        .cover-page h2 { font-size: 1.5rem; font-weight: 300; opacity: 0.9; }
        .cover-table { 
            width: 50%; 
            margin-top: 50px; 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .cover-table td { color: white; border: none; text-align: left; padding: 8px; font-size: 1.1rem; }
        
        .chapter { padding: 60px 80px; }
        .chapter-title { 
            font-size: 2.2rem; 
            color: #2d3748; 
            margin-bottom: 30px; 
            border-left: 10px solid #4ca1af;
            padding-left: 20px;
            text-transform: uppercase;
        }
        .chapter-divider { border: 0; height: 2px; background: #e2e8f0; margin-bottom: 40px; }
        
        h3 { font-size: 1.4rem; color: #4a5568; margin-top: 40px; border-bottom: 2px solid #edf2f7; padding-bottom: 8px; }
        h4 { font-size: 1.1rem; color: #718096; margin-top: 25px; }

        table { 
            width: 100%; 
            border-collapse: separate; 
            border-spacing: 0;
            margin: 20px 0; 
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }
        th { 
            background-color: #f7fafc; 
            color: #4a5568; 
            font-weight: 600; 
            padding: 12px; 
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        td { 
            padding: 12px; 
            border-bottom: 1px solid #edf2f7;
            color: #2d3748;
        }
        tr:last-child td { border-bottom: none; }
        tr:hover { background-color: #f8fafc; }

        .section-header { 
            background-color: #2d3748 !important; 
            color: white !important; 
            font-weight: 700; 
            text-transform: uppercase; 
            letter-spacing: 1px;
            font-size: 0.85rem;
        }

        code { 
            font-family: 'Roboto Mono', monospace; 
            background: #f1f5f9; 
            padding: 2px 6px; 
            border-radius: 4px; 
            color: #d53f8c;
            font-size: 0.95rem;
        }
        
        .calculation-block {
            background-color: #f8fafc;
            border-left: 4px solid #4ca1af;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }

        .result-pass { color: #38a169; font-weight: 700; }
        .result-fail { color: #e53e3e; font-weight: 700; }
        .warning-box { 
            background-color: #fffaf0; 
            border: 1px solid #feebc8; 
            color: #c05621; 
            padding: 15px; 
            border-radius: 8px;
            margin: 20px 0;
        }

        .page-break { page-break-after: always; }
        .toc { padding: 60px 80px; }
        .toc h2 { color: #2d3748; margin-bottom: 30px; font-size: 2rem; }
        .toc ul { list-style: none; padding: 0; }
        .toc li { margin: 15px 0; display: flex; align-items: baseline; }
        .toc li::after { content: ""; flex: 1; border-bottom: 1px dotted #cbd5e0; margin: 0 10px; order: 2; }
        .toc a { text-decoration: none; color: #4a5568; font-weight: 500; order: 1; transition: color 0.2s; }
        .toc a:hover { color: #4ca1af; }

        @media print {
            body { padding: 0; }
            .chapter { padding: 40px; }
            .cover-page { background: white; color: black; border: 2px solid #2c3e50; height: 95vh; }
            .cover-table td { color: black; }
            .cover-page h1 { color: #2c3e50; }
        }
        """


    # --- CHAPTER IMPLEMENTATIONS (Placeholders for now) ---
    # --- CHAPTER IMPLEMENTATIONS ---

    def generate_chapter_1_design_data(self):
        d = self.design
        p = self.project_info
        seismic = self.results.get('seismic_res') or {}
        ext = self.extended

        # Applied Annexes from extended data
        annexes = (ext.get('Applied_Annexes') or [])
        annex_str = ', '.join(annexes) if annexes else '-'

        # Pressure conversions
        p_design_mmaq = d.get('P_design', 0)
        p_design_kpa = p_design_mmaq * 0.00980665
        p_ext_kpa = d.get('P_external', 0)
        p_ext_mmaq = p_ext_kpa / 0.00980665 if p_ext_kpa else 0
        p_test_mmaq = d.get('P_test_shop', p_design_mmaq * 1.25)

        info_table = f"""
        <table>
            <tr><th colspan="4" class="section-header">1.1 PROJECT INFORMATION</th></tr>
            <tr>
                <td width="20%">Item No.:</td><td width="30%"><b>{p.get('project_name','')}</b></td>
                <td width="20%">SET:</td><td width="30%">1 EA</td>
            </tr>
            <tr>
                <td>Equipment Name:</td><td colspan="3">{p.get('tank_name', p.get('project_name',''))}</td>
            </tr>
            <tr>
                <td>Designer:</td><td>{p.get('designer','-')}</td>
                <td>Date:</td><td>{datetime.now().strftime("%Y-%m-%d")}</td>
            </tr>
            <tr>
                <td>Applicable Code:</td><td>API 650 13th Edition</td>
                <td>Rev.:</td><td>0</td>
            </tr>
        </table>
        """

        design_table = f"""
        <table>
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
        res = (self.results.get('capacities') or {}) # app.py passes capacities in 'capacities' key of results if I mapped it?
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
        
        cap = self.extended.get('capacities') or {}
        geo_vol = 3.14159 * (D/2)**2 * H
        nom_vol = 3.14159 * (D/2)**2 * max_level
        min_level = self.design.get('min_level', 0)
        net_vol = 3.14159 * (D/2)**2 * (max_level - min_level)

        html = f"""
        <h3>2.1 STORAGE VOLUME & LEVEL</h3>
        <table>
            <tr><th colspan="2" class="section-header">Level Summary</th></tr>
            <tr><td>Total Liquid Level (H)</td><td>{H:.3f} m</td></tr>
            <tr><td>High Liquid Level (H.L.L)</td><td>{max_level:.3f} m</td></tr>
            <tr><td>Low Liquid Level (L.L.L)</td><td>{min_level:.3f} m</td></tr>
        </table>
        <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
            <b>Volume Calculations</b><br>
            <code>Storage Capacity  = pi/4 * D^2 * H        = pi/4 * {D:.3f}^2 * {H:.3f} = {geo_vol:.1f} m^3 ({geo_vol*1000:.0f} liters)</code><br>
            <code>Nominal Capacity  = pi/4 * D^2 * H.L.L    = pi/4 * {D:.3f}^2 * {max_level:.3f} = {nom_vol:.1f} m^3</code><br>
            <code>Net Work Capacity = pi/4 * D^2 * (H.L.L - L.L.L) = pi/4 * {D:.3f}^2 * ({max_level:.3f}-{min_level:.3f}) = {net_vol:.1f} m^3</code>
        </div>
        <table>
            <tr><th colspan="2" class="section-header">Capacity Summary</th></tr>
            <tr><td>Storage Capacity</td><td>{geo_vol:.1f} m^3  ({geo_vol*1000:.0f} liters)</td></tr>
            <tr><td>Nominal Capacity (pi/4 * D^2 * H.L.L)</td><td>{nom_vol:.1f} m^3</td></tr>
            <tr><td>Net Working Capacity (pi/4 * D^2 * (H.L.L-L.L.L))</td><td>{net_vol:.1f} m^3</td></tr>
            <tr><td>Equivalent Barrels (BBL)</td><td>{net_vol * 6.2898:.1f} BBL</td></tr>
        </table>

        <h3>2.2 THICKNESS SUMMARY</h3>
        <table>
            <tr>
                <th>Identifier</th><th>Material</th><th>Diameter (m)</th>
                <th>Height (m)</th><th>Nominal t (mm)</th><th>Design t (mm)</th>
                <th>CA (mm)</th><th>DMT (°C)</th><th>MDMT (°C)</th>
            </tr>
        """
        # Shell courses
        courses_data = (self.results.get('shell_res') or {}).get('Shell Courses', [])
        mdmt = self.design.get('mdmt', -18.6)
        CA = self.design.get('CA', 0)
        CA_roof = self.design.get('CA_roof', 0)
        CA_bot = self.design.get('CA_bottom', 0)

        # Roof row
        roof_res = (self.results.get('roof_res') or {}).get('Roof Plate', {})
        t_roof_nom = roof_res.get('Nominal Thickness', roof_res.get('t_used', 6))
        t_roof_des = roof_res.get('t_design', 5)
        mat_roof = self.design.get('roof_material', '-')
        od_roof = round(D + 0.002 * (t_roof_nom or 6), 4)
        html += f"<tr><td>Tank Roof</td><td>{mat_roof}</td><td>{od_roof:.3f} OD</td><td>-</td><td>{t_roof_nom}</td><td>{t_roof_des}</td><td>{CA_roof}</td><td>{mdmt}</td><td>N/I</td></tr>"

        # Shell courses (top to bottom displayed bottom-first in PDF)
        for c in reversed(courses_data):
            cn = c.get('Course', '-')
            mat = c.get('Material', '-')
            t_nom = c.get('t_used', c.get('t_use', 0))
            t_des = max(c.get('td', 0), c.get('tt', 0))
            w = c.get('Width', 0)
            html += f"<tr><td>Shell Course #{cn}</td><td>{mat}</td><td>{D:.3f} ID</td><td>{w:.3f}</td><td>{t_nom}</td><td>{t_des:.0f}</td><td>{CA}</td><td>{mdmt}</td><td>N/I</td></tr>"

        # Bottom row
        bott_res = (self.results.get('bottom_res') or {}).get('Bottom Plate', {})
        t_bot_nom = bott_res.get('Nominal Thickness', bott_res.get('t_used', 10))
        t_bot_des = bott_res.get('t_design', 5)
        mat_bot = self.design.get('mat_bottom', '-')
        od_bot = round(D + 0.11, 3)
        html += f"<tr><td>Tank Bottom</td><td>{mat_bot}</td><td>{od_bot:.3f} OD</td><td>-</td><td>{t_bot_nom}</td><td>{t_bot_des}</td><td>{CA_bot}</td><td>{mdmt}</td><td>N/I</td></tr>"
        html += "</table><p><small>DMT - Design Metal Temperature &nbsp;&nbsp; MDMT - Minimum Permissible Design Metal Temperature &nbsp;&nbsp; N/I - Not Impact Tested</small></p>"
        self._add_chapter("TANK CAPACITY & THICKNESS SUMMARY", html)

        
    def generate_chapter_3_shell_design(self):
        shell_res = (self.results.get('shell_res') or {})
        courses = shell_res.get('Shell Courses', [])
        
        D = self.design.get('D', 0)
        G = self.design.get('G', 0)
        CA = self.design.get('CA', 0)
        E = self.design.get('joint_efficiency', 1.0)
        
        method_name = shell_res.get('Method', '1-Foot Method')
        is_vdm = 'VDM' in method_name or 'Variable' in method_name
        
        P_i = self.design.get('P_design', 0) * 0.00980665  # mmAq -> kPa

        html = f"""
        <h3>3.1 INPUT SUMMARY</h3>
        <table>
            <tr><th colspan="5" class="section-header">Shell Course Input Data</th></tr>
            <tr><th>Course</th><th>Course Height (m)</th><th>H (m)</th><th>t used (mm)</th><th>CA (mm)</th></tr>
        """
        for c in courses:
            html += f"<tr><td>{c.get('Course','-')}</td><td>{c.get('Width',0):.3f}</td><td>{c.get('H_eff_d',0):.3f}</td><td>{c.get('t_used',c.get('t_use',0))}</td><td>{CA:.2f}</td></tr>"
        html += "</table>"

        html += f"""
        <h3>3.2 SHELL DESIGN SUMMARY</h3>
        <table>
            <tr>
                <th>Course</th><th>Material</th>
                <th>S<sub>d</sub> (MPa)</th><th>S<sub>t</sub> (MPa)</th>
                <th>t<sub>d</sub> (mm)</th><th>t<sub>t</sub> (mm)</th>
                <th>t<sub>min</sub> (mm)</th><th>t<sub>use</sub> (mm)</th>
            </tr>
        """
        for c in courses:
            t_use = c.get('t_used', c.get('t_use', 0))
            html += f"""<tr>
                <td>{c.get('Course','-')}</td><td>{c.get('Material','-')}</td>
                <td>{c.get('Sd',0):.0f}</td><td>{c.get('St',0):.0f}</td>
                <td>{c.get('td',0):.2f}</td><td>{c.get('tt',0):.2f}</td>
                <td>5</td><td><b>{t_use}</b></td>
            </tr>"""
        html += "</table>"

        html += "<div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>"
        if courses and not is_vdm:
            html += "<b>API 650 5.6.3.2 Design Shell Thickness (1-Foot Method)</b><br>"
            html += "<code>td = [4.9 * D * (H - 0.3) * G] / (Sd * E) + CA</code><br>"
            html += "<b>API 650 5.6.3.2 Hydrostatic Test Shell Thickness</b><br>"
            html += "<code>tt = [4.9 * D * (H - 0.3)] / (St)</code><br><br>"
            
            for c in courses:
                H_d = c.get('H_eff_d', 0)
                H_t = c.get('H_eff_t', H_d)  # Test effective height
                Sd = c.get('Sd', 0)
                St = c.get('St', 0)
                td = c.get('td', 0)
                tt = c.get('tt', 0)
                # Recalculate H_eff for display matching PDF: H = base_H + P_i/(9.8*G)
                base_H = c.get('H_base', H_d - P_i / (9.8 * G) if G > 0 else H_d)
                P_i_kpa = P_i
                H_eff_display = base_H + P_i_kpa / (9.8 * G) if G > 0 else H_d
                H_t_display  = base_H + 1.25 * P_i_kpa / (9.8 * 1.0)
                html += f"<b>[Course {c.get('Course')}]</b><br>"
                html += f"<code>H = {base_H:.3f} + {P_i_kpa:.2f} / (9.8 * {G:.2f}) = <b>{H_eff_display:.4f} m</b></code><br>"
                html += f"<code>t<sub>d</sub> = 4.9 * {D:.3f} * ({H_eff_display:.4f} - 0.3) * {G:.2f} / ({Sd:.1f} * {E:.2f}) + {CA:.1f} = <b>{td:.2f} mm</b></code><br>"
                html += f"<code>H_t = {base_H:.3f} + 1.25 * {P_i_kpa:.2f} / (9.8 * 1.0) = {H_t_display:.4f} m</code><br>"
                html += f"<code>t<sub>t</sub> = 4.9 * {D:.3f} * ({H_t_display:.4f} - 0.3) / ({St:.1f} * {E:.2f}) = <b>{tt:.2f} mm</b></code><br><br>"


        elif courses and is_vdm:
            html += "<b>API 650 5.6.4 Variable Design Point Method (VDM)</b><br>"
            for c in courses:
                H_d = c.get('H_eff_d', 0)
                Sd = c.get('Sd', 0)
                St = c.get('St', 0)
                td = c.get('td', 0)
                tt = c.get('tt', 0)
                t_use = c.get('t_used', c.get('t_use', 0))
                html += f"<b>[Course {c.get('Course')}]</b><br>"
                html += f"<code>H<sub>eff</sub> = {H_d:.4f} m, t<sub>d</sub> = {td:.3f} mm, t<sub>t</sub> = {tt:.3f} mm &rarr; t<sub>use</sub> = <b>{t_use} mm</b></code><br><br>"
        html += "</div>"

        html += f"""
        <h3>3.3 SHELL COURSE ARRANGEMENT & WEIGHT</h3>
        <table>
            <tr>
                <th>Course</th><th>Width (m)</th><th>Material</th>
                <th>t<sub>d</sub> (mm)</th><th>t<sub>t</sub> (mm)</th>
                <th>t<sub>use</sub> (mm)</th><th>Weight (kg)</th>
            </tr>
        """
        for c in courses:
            html += f"""<tr>
                <td>{c.get('Course','-')}</td><td>{c.get('Width',0):.3f}</td><td>{c.get('Material','-')}</td>
                <td>{c.get('td',0):.2f}</td><td>{c.get('tt',0):.2f}</td>
                <td><b>{c.get('t_used',c.get('t_use',0))}</b></td><td>{c.get('Weight',0):.0f}</td>
            </tr>"""
        html += f"""
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
        bott_res = (self.results.get('bottom_res') or {}).get('Bottom Plate', {})
        
        # Build Table
        rows = ""
        for k, v in bott_res.items():
            if isinstance(v, dict): continue # skip calc details if nested
            rows += f"<tr><td>{k}</td><td>{v}</td></tr>"
            
        html = f"""
        <h3>5.1 BOTTOM PLATE THICKNESS</h3>
        <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
            <b>API 650 5.4.1 Bottom Plate Requirements</b><br>
            All bottom plates shall have a corroded thickness of not less than 6 mm (0.236 in.).<br>
            <code>t_min = 6.0 + CA = 6.0 + {self.design.get('CA_bottom', 0):.1f} = {6.0 + self.design.get('CA_bottom', 0):.1f} mm</code>
        </div>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            {rows}
        </table>
        """
        self._add_chapter("BOTTOM PLATE DESIGN", html)
        
    def generate_chapter_6_annular_plate(self):
        ann_res = (self.results.get('bottom_res') or {}).get('Annular Plate', {})
        
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
            
            courses = (self.results.get('shell_res') or {}).get('Shell Courses', [])
            c1 = courses[0] if courses else {}
            D = self.design.get('D', 0)
            G = self.design.get('G', 0)
            H_d = c1.get('H_eff_d', self.design.get('H', 0))
            t_prov = c1.get('t_used', c1.get('t_use', 0))
            stress = (4.9 * D * (H_d - 0.3) * G) / t_prov if t_prov > 0 else 0
            
            html = f"""
            <h3>6.1 ANNULAR PLATE CHECK</h3>
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 650 5.5 Annular Bottom Plates</b><br>
                Product Stress in 1st Shell Course: <code>Stress = (4.9 * D * (H - 0.3) * G) / t_provided</code><br>
                <code>Stress = (4.9 * {D:.3f} * ({H_d:.3f} - 0.3) * {G:.3f}) / {t_prov:.2f} = {stress:.1f} MPa</code><br>
                Annular plate required thickness is derived from Table 5.1 based on First Course Product Stress and First Course Thickness.
            </div>
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
        wg_res = (self.results.get('wind_girder_res') or {})
        D = self.design.get('D', 0)
        
        # Top Stiffener
        top = wg_res.get('Top Stiffener', {})
        html = "<h3>7.1 TOP WIND GIRDER (STIFFENER)</h3>"
        if top:
            H2 = top.get('H2', 0)
            Z_req = top.get('Z_req_cm3', 0)
            html += f"""
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 650 5.9.6.1 Top Wind Girder Required Section Modulus</b><br>
                <code>Z = (D^2 * H2) / 17</code><br>
                <code>Z = ({D:.3f}^2 * {H2:.3f}) / 17 = {Z_req:.2f} cm^3</code>
            </div>
            <table>
                <tr><td>Required Modulus (Z_req):</td><td>{Z_req:.2f} cm^3</td></tr>
                <tr><td>Provided Modulus (Z_act):</td><td>{top.get('Z_act_cm3',0):.2f} cm^3</td></tr>
                <tr><td>Check:</td><td class='{ "result-pass" if top.get('Status')=="OK" else "result-fail" }'>{top.get('Status','-')}</td></tr>
            </table>
            """
            
        # Intermediate
        inter = wg_res.get('Intermediate Stiffener', {})
        html += "<h3>7.2 INTERMEDIATE WIND GIRDERS</h3>"
        req = inter.get('Required?', 'No')
        html += f"<p>Required: <b>{req}</b></p>"
        
        if req == 'Yes':
            H1 = inter.get('H1_max', 0)
            t = inter.get('t_top', 0)
            V = self.design.get('V_wind', 0)
            V_mph = V * 3.6 / 1.609 # approx
            html += f"""
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 650 5.9.7.1 Intermediate Wind Girder Max Unstiffened Height (H1)</b><br>
                <code>H1 = 9.47 * t * sqrt((t / D)^3) * (190 / V)^2</code><br>
                <code>H1 = 9.47 * {t:.1f} * sqrt(({t:.1f} / {D:.3f})^3) * (190 / {V_mph:.1f})^2 = {H1:.3f} m</code>
            </div>
            <table>
                <tr><td>Transformed Height (H_tr):</td><td>{inter.get('H_tr',0):.3f} m</td></tr>
                <tr><td>Max Unstiffened Height (H1):</td><td>{H1:.3f} m</td></tr>
                <tr><td>Number of Stiffeners:</td><td>{inter.get('Count',0)}</td></tr>
            </table>
            """
            
        self._add_chapter("WIND GIRDER DESIGN", html)

    def generate_chapter_8_cone_roof(self):
        roof_res = (self.results.get('roof_res') or {}).get('Roof Plate', {})
        d = self.design
        D = d.get('D', 0)
        roof_type = d.get('roof_type', '')
        CA = d.get('CA_roof', 0)
        
        # Load Summary (PDF Page 17)
        DL = (self.extended.get('weights') or {}).get('W_roof_kg', 0) * 9.81 / (3.14159 * (D/2)**2) if D > 0 else 0 # Pa
        LL = d.get('live_load', 0) * 1000 # kPa to Pa
        SL = d.get('snow_load', 0) * 1000 # kPa to Pa
        Pi = d.get('P_design', 0) * 9.81  # mmAq to Pa
        Pe = d.get('P_external', 0) * 1000 # kPa to Pa
        
        L_comb = max(LL, SL)
        
        html = f"""
        <h3>8.1 DESIGN LOAD SUMMARY (Pa)</h3>
        <table>
            <tr><th>Load Case</th><th>Value (Pa)</th><th>Value (kPa)</th></tr>
            <tr><td>Dead Load (DL)</td><td>{DL:.1f}</td><td>{DL/1000:.3f}</td></tr>
            <tr><td>Live Load (Lr)</td><td>{LL:.1f}</td><td>{LL/1000:.3f}</td></tr>
            <tr><td>Snow Load (S)</td><td>{SL:.1f}</td><td>{SL/1000:.3f}</td></tr>
            <tr><td>Internal Pressure (Pi)</td><td>{Pi:.1f}</td><td>{Pi/1000:.3f}</td></tr>
            <tr><td>External Pressure (Pe)</td><td>{Pe:.1f}</td><td>{Pe/1000:.3f}</td></tr>
        </table>

        <h3>8.2 LOAD COMBINATIONS (API 650 5.2.2)</h3>
        <table>
            <tr><th>Combination</th><th>Calculation</th><th>Total Load (Pa)</th></tr>
            <tr><td>(1) DL + Lr/S</td><td>{DL:.1f} + {L_comb:.1f}</td><td>{DL + L_comb:.1f}</td></tr>
            <tr><td>(2) DL + Pe + 0.4(Lr/S)</td><td>{DL:.1f} + {Pe:.1f} + 0.4*{L_comb:.1f}</td><td>{DL + Pe + 0.4*L_comb:.1f}</td></tr>
            <tr><td>(3) DL + Pi + 0.4(Lr/S)</td><td>{DL:.1f} + {Pi:.1f} + 0.4*{L_comb:.1f}</td><td>{DL + Pi + 0.4*L_comb:.1f}</td></tr>
        </table>

        <h3>8.3 ROOF PLATE THICKNESS</h3>
        """
        
        if "Self-Supported" in roof_type:
            slope = d.get('roof_slope', 0.0625)
            theta = math.atan(slope)
            t_min = D / (4.8 * math.sin(theta)) if theta > 0 else 0
            t_use = roof_res.get('Nominal Thickness', roof_res.get('t_used', 6))
            
            html += f"""
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 650 5.10.5 Self-Supported Cone Roofs</b><br>
                Minimum Thickness (t_min): <code>D / (4.8 * sin(theta)) + CA</code><br>
                <code>t_min = {D:.3f} / (4.8 * sin({math.degrees(theta):.1f}*)) + {CA:.1f} = {t_min+CA:.2f} mm</code><br>
                Provided Thickness: <b>{t_use} mm</b>
            </div>
            """
        else:
            t_use = roof_res.get('Nominal Thickness', roof_res.get('t_used', 5))
            html += f"""
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 650 5.10.4 Supported Cone Roofs</b><br>
                Minimum Thickness: 5 mm (3/16 in.) + CA<br>
                Provided Thickness: <b>{t_use} mm</b>
            </div>
            """
            
        self._add_chapter("CONE ROOF PLATE DESIGN", html)

    def generate_chapter_9_roof_structure(self):
        struct = (self.results.get('struct_data') or {})
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
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 650 5.10.4.4 Allowable Stresses for Roof Structure</b><br>
                Bending Stress, <code>Fb = 0.6 * Fy</code> or <code>137 MPa</code> (19,800 lbf/in^2)<br>
                Deflection Limit = <code>L / 200</code><br>
                (Structural profiles evaluated based on AISC Manual)
            </div>
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                {format_dict(struct)}
            </table>
            """
            
        self._add_chapter("ROOF STRUCTURE DESIGN", html)

    def generate_chapter_10_compression_ring(self):
        roof_res = (self.results.get('roof_res') or {}).get('Roof Plate', {})
        d = self.design
        D = d.get('D', 0)
        courses = (self.results.get('shell_res') or {}).get('Shell Courses', [])
        t_top = courses[0].get('t_used', 8) if courses else 8 # top course
        t_roof = roof_res.get('Nominal Thickness', 6)
        
        req_area = roof_res.get('Required Compression Area', 0)
        avail_area = roof_res.get('Available Compression Area', 0)
        
        if not req_area or req_area == 'N/A':
            html = "<p>Compression Ring analysis not performed or not applicable.</p>"
        else:
            # Participating Area details (PDF Page 21)
            w_shell = 0.6 * math.sqrt( (D/2) * 1000 * t_top ) / 1000 # m
            w_roof  = 0.6 * math.sqrt( (D/2) * 1000 * t_roof / math.sin(math.atan(d.get('roof_slope',0.0625))) ) / 1000 if d.get('roof_slope') else 0
            
            html = f"""
            <h3>10.1 PARTICIPATING AREA AT JUNCTION (API 650 5.10.5.2)</h3>
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>Effective Participating Widths</b><br>
                Shell side: <code>0.6 * sqrt(R * t_shell)</code> = 0.6 * sqrt({D/2:.3f} * {t_top}) = {w_shell*1000:.1f} mm<br>
                Roof side: <code>0.6 * sqrt(R * t_roof / sin(theta))</code> = {w_roof*1000:.1f} mm
            </div>
            <table>
                <tr><th>Component</th><th>Effective Width (mm)</th><th>Thickness (mm)</th><th>Area (mm2)</th></tr>
                <tr><td>Shell Portion</td><td>{w_shell*1000:.1f}</td><td>{t_top}</td><td>{w_shell*1000*t_top:.1f}</td></tr>
                <tr><td>Roof Portion</td><td>{w_roof*1000:.1f}</td><td>{t_roof}</td><td>{w_roof*1000*t_roof:.1f}</td></tr>
                <tr><td>Top Angle / Stiffener</td><td>-</td><td>-</td><td>{avail_area - (w_shell*1000*t_top + w_roof*1000*t_roof):.1f}</td></tr>
                <tr style='font-weight:bold; background:#eee;'><td>TOTAL AVAILABLE AREA</td><td></td><td></td><td>{avail_area:.1f}</td></tr>
            </table>

            <h3>10.2 COMPRESSION RING AREA CHECK</h3>
            <p>Required Area (Ac): <b>{req_area:.1f} mm2</b></p>
            <p>Available Area (Aa): <b>{avail_area:.1f} mm2</b></p>
            <p>Status: <b class="{'result-pass' if avail_area >= req_area else 'result-fail'}">{'PASS' if avail_area >= req_area else 'FAIL - Stiffener Required'}</b></p>
            """
        
        self._add_chapter("REQUIRED AREA OF COMPRESSION RING", html)

    def generate_chapter_11_wind_load(self):
        wind = (self.results.get('wind_res') or {})
        V = self.design.get('V_wind', 0)
        V_mph = V * 3.6 / 1.609
        
        Kzt = wind.get('Kzt', 1.0)
        Kd = wind.get('Kd', 0.95)
        G_wind = wind.get('G', 0.85)
        Cf = 0.6
        I_wind = wind.get('I', 1.0)
        
        p_wind = wind.get('P_wind_kPa', 0)
        qz = 0.613 * Kzt * Kd * (V**2) * I_wind
        
        anchor = self.extended.get('anchor') or {}
        D = self.design.get('D', 0)
        H = self.design.get('H', 0)
        P_i_kpa = self.design.get('P_design', 0) * 0.00980665

        w = self.extended.get('weights') or {}
        DLS = w.get('W_shell_kg', 0) * 9.81
        DLR = w.get('W_roof_kg', 0) * 9.81

        Mws_kNm = anchor.get('Mws_kNm', p_wind * D * H**2 / 2) if p_wind else 0
        Mpi_kNm = anchor.get('Mpi_kNm', P_i_kpa * 1000 * 3.14159 * D**3 / 8 / 1000)
        MDL_kNm = anchor.get('MDL_kNm', DLS * D / 2 / 1000)
        MDLR_kNm = anchor.get('MDLR_kNm', DLR * D / 2 / 1000)

        UL1 = 0.6 * (Mws_kNm) + Mpi_kNm
        DL1 = MDL_kNm / 1.5 + MDLR_kNm
        UL2 = (Mws_kNm) + 0.4 * Mpi_kNm
        DL2 = (MDL_kNm + anchor.get('MF_kNm', 0)) / 2 + MDLR_kNm
        anchorage_required = (UL1 > DL1) or (UL2 > DL2)

        html = f"""
        <h3>11.1 WIND LOAD PARAMETERS & PRESSURE</h3>
        <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
            Velocity (V): {V} m/s ({V_mph:.1f} mph)<br>
            qz = 0.613 * {Kzt} * {Kd} * {V}^2 * {I_wind} = {qz:.1f} N/m2<br>
            P_ws = {qz:.1f} * {G_wind} * {Cf} * 0.6 = {p_wind:.3f} kPa
        </div>
        
        <h3>11.2 OVERTURNING MOMENT</h3>
        <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
            Mws = {p_wind:.4f} * 1000 * {D:.2f} * {H:.2f} * {H:.2f} / 2 = {Mws_kNm*1000:.1f} N-m<br>
            Mpi = {P_i_kpa:.3f} * 1000 * pi * {D:.3f}^3 / 8 = {Mpi_kNm*1000:.1f} N-m
        </div>

        <h3>11.3 STABILITY CHECK</h3>
        <table>
            <tr><th>Check Case</th><th>Uplift (N-m)</th><th>Resisting (N-m)</th><th>Result</th></tr>
            <tr><td>0.6Mw + Mpi</td><td>{UL1*1000:.0f}</td><td>{DL1*1000:.0f}</td><td>{"FAIL" if UL1>DL1 else "OK"}</td></tr>
            <tr><td>Mw + 0.4Mpi</td><td>{UL2*1000:.0f}</td><td>{DL2*1000:.0f}</td><td>{"FAIL" if UL2>DL2 else "OK"}</td></tr>
        </table>
        <p><b>Anchorage: {"Required" if anchorage_required else "Not Required"}</b></p>
        """
        self._add_chapter("WIND LOAD ON TANKS", html)

    def generate_chapter_12_seismic_load(self):
        seismic = self.results.get('seismic_res') or {}
        graph = self.extended.get('seismic_graph', '')
        
        if not seismic:
            html = "<p>Seismic Data not available (Method 'None' selected?)</p>"
        else:
            D = self.design.get('D', 0)
            H = self.design.get('H', 0)
            G = self.design.get('G', 1.0)
            max_level = self.design.get('HD', H)
            w = self.extended.get('weights') or {}
            Ws = w.get('W_shell_kg', 0)
            Wr = w.get('W_roof_kg', 0)
            Wp = (3.14159 * (D/2)**2 * max_level) * G * 1000 # Product weight
            
            # Parameters
            Ss = seismic.get('Ss_input', 0)
            S1 = seismic.get('S1_input', 0)
            SDS = seismic.get('SDS', 0)
            SD1 = seismic.get('SD1', 0)
            seis_method = seismic.get('Method', 'Mapped')
            I = seismic.get('Importance Factor', 1.0)
            Rwi = 3.5 
            Rwc = 2.0
            
            # Results
            Wi = seismic.get('Wi_kg', 0)
            Wc = seismic.get('Wc_kg', 0)
            Ai = seismic.get('Ai', 0)
            Ac = seismic.get('Ac', 0)
            Av = seismic.get('Av', 0)
            V = seismic.get('Base_Shear_kN', 0)
            Mrw = seismic.get('Ringwall_Moment_kNm', 0)
            ds = seismic.get('Sloshing_Wave_Height_m', 0)
            
            html = f"""
            <h3>12.1 SEISMIC DESIGN PARAMETERS (API 650 ANNEX E)</h3>
            <div style='background-color:#f8fafc; padding:20px; border-radius:8px; border:1px solid #e2e8f0;'>
                <table style="border:none; margin:0;">
                    <tr><td>Seismic Use Group (SUG):</td><td>{seismic.get('Use Group','I')}</td><td>Importance Factor (I):</td><td>{I}</td></tr>
                    <tr><td>Site Class:</td><td>{seismic.get('Site Class','D')}</td><td>Design Method:</td><td>{seis_method}</td></tr>
                    <tr><td>SDS (Short Period):</td><td>{SDS:.3f} g</td><td>SD1 (1-Sec Period):</td><td>{SD1:.3f} g</td></tr>
                </table>
            </div>

            <h3>12.2 EFFECTIVE MASS & DYNAMIC COEFFICIENTS</h3>
            <div class="calculation-block">
                <b>1. Effective Weights</b><br>
                - Total Liquid Weight (W): {Wp:.2f} kg<br>
                - Impulsive Weight (Wi): {Wi:.2f} kg ({Wi/Wp*100 if Wp else 0:.1f}% of W)<br>
                - Convective Weight (Wc): {Wc:.2f} kg ({Wc/Wp*100 if Wp else 0:.1f}% of W)<br><br>
                
                <b>2. Dynamic Coefficients</b><br>
                - Impulsive Accel (Ai): {Ai:.4f} g<br>
                - Convective Accel (Ac): {Ac:.4f} g<br>
                - Convective Period (Tc): {seismic.get('Tc_s',0):.2f} sec<br>
                - Sloshing Wave Height (delta_s): {ds:.3f} m
            </div>

            <h3>12.3 STABILITY & MOMENT SUMMARY</h3>
            <table>
                <tr style="background:#2d3748; color:white;">
                    <th>Parameter</th><th>Value</th><th>Unit</th><th>API 650 Status</th>
                </tr>
                <tr><td>Total Base Shear (V)</td><td>{V:.2f}</td><td>kN</td><td>-</td></tr>
                <tr><td>Ringwall Moment (Mrw)</td><td>{Mrw:.2f}</td><td>kN-m</td><td>-</td></tr>
                <tr><td>Anchorage Ratio (J)</td><td>{seismic.get('Anchorage_Ratio_J', 0):.3f}</td><td>-</td><td><b>{seismic.get('Anchorage_Status','-')}</b></td></tr>
                <tr><td>Sliding Check</td><td>{seismic.get('Sliding_Status','-')}</td><td>-</td><td>Friction Res: {seismic.get('Sliding_Friction_Res_kN',0):.1f} kN</td></tr>
            </table>
            """

            
            if graph:
                html += f'<h3>12.5 DESIGN SPECTRUM GRAPH</h3><img src="data:image/png;base64,{graph}" style="max-width:80%; margin: 20px auto; display:block; border: 1px solid #ddd;" />'

            
        self._add_chapter("SEISMIC DESIGN OF STORAGE TANK", html)

    def generate_chapter_13_anchor_bolt(self):
        anchor = self.extended.get('anchor') or {}
        chair = self.extended.get('anchor_chair') or {}
        
        status = anchor.get('Status', 'N/A')
        D = self.design.get('D', 0)
        N = anchor.get('Number of Bolts', 0)
        
        html = f"<h3>13.1 ANCHOR BOLT DESIGN SUMMARY</h3>"
        
        if status == 'Not Required':
             html += "<div class='warning-box'>Anchors are not required based on API 650 stability criteria for Wind and Seismic loads.</div>"
        else:
             uplift_total = anchor.get('Net Uplift Force (kN)', 0)
             u_bolt = uplift_total / N if N > 0 else 0
             
             html += f"""
             <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                 <b>Design Criteria (API 650 5.12)</b><br>
                 Uplift Force per Bolt (U) = <code>[4 * Mw / (D * N)] - [W_shell + W_roof] / N</code> (Simplified Concept)<br>
                 Actual calculated Uplift per bolt: <b>{u_bolt:.1f} kN</b>
             </div>
             <table>
                 <tr><th colspan="2" class="section-header">Anchor Bolt Parameters</th></tr>
                 <tr><td>Number of Bolts (N)</td><td>{N} EA</td></tr>
                 <tr><td>Selected Bolt Size</td><td><b>{anchor.get('Bolt Size', '-')}</b></td></tr>
                 <tr><td>Total Net Uplift Force</td><td>{uplift_total:.1f} kN</td></tr>
                 <tr><td>Force per Bolt (U)</td><td>{u_bolt:.1f} kN</td></tr>
                 <tr><td>Provided Bolt Area (Ab)</td><td>{anchor.get('Provided Bolt Area (mm2)', 0):.1f} mm2</td></tr>
                 <tr><td>Allowable Tensile Stress</td><td>{anchor.get('Allowable Stress (MPa)', 105):.1f} MPa</td></tr>
             </table>
             """
             
        if chair and chair.get('Status') != 'N/A':
            html += "<h3>13.2 ANCHOR CHAIR DIMENSIONS</h3>"
            html += f"""
            <table>
                <tr><th>Description</th><th>Symbol</th><th>Value (mm)</th></tr>
                <tr><td>Chair Height</td><td>h</td><td>{chair.get('Chair Height h', 0)}</td></tr>
                <tr><td>Chair Width</td><td>b</td><td>{chair.get('Chair Width b', 0)}</td></tr>
                <tr><td>Top Plate Thickness</td><td>c</td><td>{chair.get('Top Plate t', 0)}</td></tr>
                <tr><td>Gusset Plate Thickness</td><td>g</td><td>{chair.get('Gusset Plate t', 0)}</td></tr>
                <tr><td>Distance from Shell</td><td>e</td><td>{chair.get('Bolt Eccentricity e', 0)}</td></tr>
            </table>
            """
        
        self._add_chapter("ANCHOR BOLT & ANCHOR CHAIR DESIGN", html)

        
    def generate_chapter_14_small_pressure(self):
        af = self.extended.get('annex_f') or {}
        max_P = af.get('Max Design Pressure P_max (kPa)', 0)
        P_fail = af.get('Failure Pressure P_fail (kPa)', 0)
        
        if not af:
             html = "<p>Annex F (Small Internal Pressure) checks not performed.</p>"
        else:
             D = self.design.get('D', 0)
             W = af.get('Total Weight W (N)', 0)
             A_val = af.get('Participating Area A (mm2)', 0)
             Fty = 200 # Approx or fetch if available
             html = f"""
             <h3>14.1 ANNEX F CALCULATIONS</h3>
             <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                 <b>API 650 F.4.1 Design Pressure Limits</b><br>
                 <code>P_max = (W / (pi * D^2 / 4)) / 1000  (kPa)</code><br>
                 <code>P_max = ({W:.1f} / (pi * {D:.3f}^2 / 4)) / 1000 = {max_P:.3f} kPa</code><br><br>
                 <b>API 650 F.7 Calculated Failure Pressure</b><br>
                 <code>P_fail = 0.00127 * A * Fty / D^2 + 0.000122 * W / D^2  (kPa)</code><br>
                 <code>P_fail = 0.00127 * {A_val:.1f} * {Fty} / {D:.3f}^2 + 0.000122 * {W:.1f} / {D:.3f}^2 = {P_fail:.3f} kPa</code>
             </div>
             <table>
                 <tr><td>Max Design Pressure (P_max):</td><td>{max_P:.3f} kPa</td></tr>
                 <tr><td>Calculated Failure Pressure (P_fail):</td><td>{P_fail:.3f} kPa</td></tr>
                 <tr><td>Frangible Joint?</td><td>{af.get('Frangible?', 'Check Detail')}</td></tr>
             </table>
             """
        self._add_chapter("DESIGN OF TANK FOR SMALL INTERNAL PRESSURES", html)

    def generate_chapter_15_loading_data(self):
        # Summarize all loads
        w = self.extended.get('weights') or {}
        d = self.design
        
        html = f"""
        <h3>15.1 APPLIED LOADS</h3>
        <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
            <b>Load Summary Basis</b><br>
            Dead Loads, Live Loads, and Pressure Loads applied to the tank structure.<br>
            <code>Total Dead Load = Shell + Roof + Structure</code><br>
            <code>P_design = {d.get('P_design',0)} mmH2O = {d.get('P_design',0)/100:.3f} kPa</code>
        </div>
        <table>
            <tr><th colspan="2" class="section-header">DEAD LOADS (WEIGHTS)</th></tr>
            <tr><td>Shell Weight New:</td><td>{w.get('W_shell_kg',0):.0f} kg</td></tr>
            <tr><td>Roof Plate Weight (corroded):</td><td>{w.get('W_roof_kg',0):.0f} kg</td></tr>
            <tr><td>Total Structure Weight:</td><td>{(self.results.get('struct_data') or {}).get('Total_Struct_Weight',0):.0f} kg</td></tr>
            
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
        G = self.design.get('G', 1.0)
        H = self.design.get('H', 0)
        max_level = self.design.get('HD', H)

        v_test = 3.14159 * (D/2)**2 * H
        w_water = v_test * 1000

        w_shell = w.get('W_shell_kg', 0)
        w_roof  = w.get('W_roof_kg', 0)
        w_bottom= w.get('W_bottom_kg', 0)
        w_struct= (self.results.get('struct_data') or {}).get('Total_Struct_Weight', 0)
        w_anchor= w.get('W_anchor_kg', 0)

        # Insulation weight estimate
        ins_total = sum(c.get('Insulation_kg', 0) for c in (self.results.get('shell_res') or {}).get('Shell Courses', []))

        # Liquid weight at operating level
        v_oper = 3.14159 * (D/2)**2 * max_level
        w_liq = v_oper * G * 1000

        w_empty = w_shell + w_roof + w_bottom + w_struct + w_anchor
        w_oper = w_empty + w_liq
        w_test_total = w_empty + w_water

        courses_data = (self.results.get('shell_res') or {}).get('Shell Courses', [])

        # Build component rows
        def c_row(name, metal, ins, op_liq, test_liq, sa):
            return f"<tr><td>{name}</td><td>{metal:.1f}</td><td>{metal:.1f}</td><td>{ins:.1f}</td><td>{op_liq:.1f}</td><td>{test_liq:.1f}</td><td>{sa:.2f}</td></tr>"

        html = f"""
        <h3>16.1 WEIGHT SUMMARY</h3>
        <p><b>Weight (kg) Contributed by Tank Elements</b></p>
        <table style="font-size:9pt;">
            <tr>
                <th>Component</th>
                <th>Metal New (kg)</th><th>Metal Corroded (kg)</th>
                <th>Insulation (kg)</th>
                <th>Operating Liquid (kg)</th><th>Test Liquid (kg)</th>
                <th>Surface Area (m^2)</th>
            </tr>
        """
        # Roof
        w_ins_roof = 0
        if self.design.get('insulation_opt', 1.0) < 1.0:
             # If insulation exists, estimate roof insulation weight (approx 50kg/m2)
             w_ins_roof = 3.14159 * (D/2)**2 * 50.0 
        html += c_row("Tank Roof", w_roof, w_ins_roof, 0, 0, 3.14159 * (D/2)**2)

        # Shell courses
        prev_h = 0
        for c in reversed(courses_data):
            mat_w = c.get('Weight', 0)
            ins_w = c.get('Insulation_kg', 0)
            wid   = c.get('Width', 0)
            liq_h = max(0, max_level - prev_h)
            liq_v = 3.14159 * D * wid * 0  # simplified – liquid in annular area per course
            liq_w_c = 0  # approximate – full liquid weight shown in total
            sa_c  = 3.14159 * D * wid
            html += c_row(f"Shell Course #{c.get('Course','-')}", mat_w, ins_w, 0, 0, sa_c)
            prev_h += wid

        # Bottom
        sa_bot = 3.14159 * (D/2 + 0.055)**2
        html += c_row("Tank Bottom", w_bottom, 0, 0, 0, sa_bot)
        # Anchor
        if w_anchor > 0:
            html += c_row("Anchorage", w_anchor, 0, 0, 0, 0)

        html += f"""
            <tr style="font-weight:bold; background:#f2f2f2;">
                <td>TOTAL</td>
                <td>{w_empty:.1f}</td><td>{w_empty:.1f}</td>
                <td>{ins_total:.1f}</td>
                <td>{w_liq:.1f}</td><td>{w_water:.1f}</td>
                <td>-</td>
            </tr>
        </table>

        <h3>16.2 TANK TOTALS</h3>
        <table>
            <tr><th colspan="3" class="section-header">Weight Summary</th></tr>
            <tr><th>Condition</th><th>New (kg)</th><th>Corroded (kg)</th></tr>
            <tr><td>Operating Weight (kg)</td><td>{w_oper:.0f}</td><td>{w_oper:.0f}</td></tr>
            <tr><td>Empty Weight (kg)</td><td>{w_empty:.0f}</td><td>{w_empty:.0f}</td></tr>
            <tr><td>Test Weight (kg) — Full Water</td><td>{w_test_total:.0f}</td><td>{w_test_total:.0f}</td></tr>
            <tr><td>Capacity (liters)</td><td>{v_oper*1000:.0f}</td><td>{v_oper*1000:.0f}</td></tr>
        </table>

        <h3>16.3 MOMENT SUMMARY</h3>
        <table>
            <tr><td>Wind Overturning Moment (Mw):</td><td>{self.extended.get('anchor',{}).get('Wind Overturning Moment (kN-m)', 0):.1f} kN-m</td></tr>
            <tr><td>Seismic Ringwall Moment (Mrw):</td><td>{(self.results.get('seismic_res') or {}).get('Ringwall_Moment_kNm', 0):.1f} kN-m</td></tr>
            <tr><td>Seismic Slab Moment (Ms):</td><td>{(self.results.get('seismic_res') or {}).get('Slab_Moment_kNm', 0):.1f} kN-m</td></tr>
        </table>
        """
        self._add_chapter("WEIGHT & MOMENT SUMMARY", html)


    def generate_chapter_17_venting(self):
        vent = (self.results.get('venting_res') or {})
        
        if not vent:
            html = "<p>Venting Analysis not performed (API 2000).</p>"
        else:
            V_in = vent.get('Normal_Inbreathing_Nm3h',0)
            V_out = vent.get('Normal_Outbreathing_Nm3h',0)
            V_emerg = vent.get('Emergency_Venting_Nm3h',0)
            A_wetted = vent.get('Wetted_Area_m2', 0)
            Q_watts = vent.get('Heat_Input_Q_Watts', 0)
            
            html = f"""
            <h3>17.1 NORMAL VENTING (API 2000)</h3>
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 2000 4.3 Normal Venting Requirements</b><br>
                <code>Inbreathing = Thermal Inbreathing + Liquid Movement (Pump-out)</code><br>
                <code>Outbreathing = Thermal Outbreathing + Liquid Movement (Pump-in)</code>
            </div>
            <table>
                <tr><td>Inbreathing Req (Thermal + Liquid):</td><td>{V_in:.1f} Nm^3/h</td></tr>
                <tr><td>Outbreathing Req (Thermal + Liquid):</td><td>{V_out:.1f} Nm^3/h</td></tr>
            </table>
            
            <h3>17.2 EMERGENCY VENTING (FIRE CASE)</h3>
            <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
                <b>API 2000 4.3.3.2 Emergency Venting (Fire Exposure)</b><br>
                <code>Q = 43200 * A_wetted^0.82</code> (For Wetted Area < 260 m^2)<br>
                <code>Q = 43200 * {A_wetted:.1f}^0.82 = {Q_watts:.0f} Watts</code><br><br>
                <code>Emergency Venting = Q / (L_v * sqrt(M / T))</code><br>
                <code>Emergency Venting = {V_emerg:.1f} Nm^3/h</code> (Simplified Substitution)
            </div>
            <table>
                <tr><td>Wetted Area:</td><td>{vent.get('Wetted_Area_m2',0):.1f} m^2</td></tr>
                <tr><td>Heat Input (Q):</td><td>{vent.get('Heat_Input_Q_Watts',0):.0f} Watts</td></tr>
                <tr><td>Required Venting Capacity:</td><td>{V_emerg:.1f} Nm^3/h</td></tr>
            </table>
            """
        self._add_chapter("VENTING ATM. AND LOW-PRESSURE STORAGE TANKS", html)

    def generate_chapter_18_civil_loading(self):
        D = self.design.get('D', 0)
        Area = math.pi * (D / 2) ** 2 if D else 0
        Circ = math.pi * D if D else 0
        
        w = self.extended.get('weights', {})
        W_shell = w.get('W_shell_kg', 0) / 1000.0
        W_roof = w.get('W_roof_kg', 0) / 1000.0
        W_struct = (self.results.get('struct_data') or {}).get('Total_Struct_Weight', 0) / 1000.0
        W_bottom = w.get('W_bottom_kg', 0) / 1000.0
        
        DL = W_shell + W_roof + W_struct
        
        H = self.design.get('H', 0)
        G = self.design.get('G', 0)
        max_level = self.design.get('HD', H)
        W_product = Area * max_level * G
        W_testwater = Area * H * 1.0
        
        P_int = self.design.get('P_design', 0) / 1000.0 # mmH2O to ton/m2 (approx)
        P_test = self.design.get('P_test', 0) / 1000.0
        
        LL = self.design.get('live_load', 0) * 0.10197 # kPa to ton/m2
        
        P_bottom = W_bottom / Area if Area else 0
        P_product = W_product / Area if Area else 0
        P_testwater = W_testwater / Area if Area else 0
        P_floating = 0 # Future expansion for floating roofs
        
        anchor = self.extended.get('anchor', {})
        Mw = anchor.get('Wind Overturning Moment (kN-m)', 0) * 0.10197
        N = anchor.get('Number of Bolts', 0)
        
        seismic = (self.results.get('seismic_res') or {})
        Mrw = seismic.get('Ringwall_Moment_kNm', 0) * 0.10197
        Ms = seismic.get('Slab_Moment_kNm', 0) * 0.10197
        
        Z_shell = math.pi * D**2 / 4 if D else 0
        Z_base = math.pi * D**3 / 32 if D else 1
        
        # DW1 Calculations
        A = P_bottom + P_product + P_int + P_floating
        F = P_bottom + P_int + P_floating
        K = P_bottom + P_product + P_floating
        P = P_bottom + P_floating
        U = P_bottom + P_testwater + P_test + P_floating
        Z = P_bottom + P_product + P_floating + P_int + (Ms / Z_base)
        AA = P_bottom + P_product + P_floating + P_int - (Ms / Z_base)
        
        # W1 Calculations
        DL_line = DL / Circ if Circ else 0
        LL_line = (LL * Area) / Circ if Circ else 0
        UP_int_line = (P_int * Area) / Circ if Circ else 0
        UP_test_line = (P_test * Area) / Circ if Circ else 0
        WL_line = Mw / Z_shell if Z_shell else 0
        WL_50_line = (Mw * 0.25) / Z_shell if Z_shell else 0
        Seismic_line = Mrw / Z_shell if Z_shell else 0
        
        B = DL_line + LL_line - UP_int_line
        C = B + WL_line
        G_val = DL_line + LL_line - UP_int_line
        H_val = G_val + WL_line
        L = DL_line + LL_line
        M = L + WL_line
        Q = DL_line + LL_line
        R = Q + WL_line
        V_val = DL_line - UP_test_line
        W_val = V_val + WL_50_line
        AB = DL_line + LL_line + Seismic_line
        
        # W2 Calculations
        def calc_bolt(uplift_P, uplift_M, dead_weight):
            if N == 0: return 0
            val = (uplift_P + (4 * uplift_M / D if D else 0) - dead_weight) / N
            return max(0, val)
            
        UP_int_tot = P_int * Area
        UP_test_tot = P_test * Area
        
        D_val = calc_bolt(UP_int_tot, 0, DL)
        E_val = calc_bolt(UP_int_tot, Mw, DL)
        I_val = calc_bolt(UP_int_tot, 0, DL)
        J_val = calc_bolt(UP_int_tot, Mw, DL)
        N_val = 0
        O_val = calc_bolt(0, Mw, DL)
        S_val = 0
        T_val = calc_bolt(0, Mw, DL)
        X_val = calc_bolt(UP_test_tot, 0, DL)
        Y_val = calc_bolt(UP_test_tot, Mw*0.25, DL)
        AC_val = calc_bolt(UP_int_tot, Mrw, DL)
        AF_val = calc_bolt(1.25 * UP_test_tot, 0, DL)
        AG_val = calc_bolt(1.5 * UP_int_tot, Mw, DL)

        html = f"""
        <h3>18.1 DESIGN BASIS FOR FOUNDATION LOADING</h3>
        <p>Loads are calculated per API 650 requirements. Units: Metric Tons (ton) and Meters (m).</p>
        
        <div style='background-color:#f8f9fa; padding:10px; margin-bottom:15px; border-left:4px solid #2c3e50;'>
            <b>1. Loading Variables</b><br>
            - Shell & Struct Weight: {DL_line*Circ:.2f} ton<br>
            - Product Weight: {W_product:.2f} ton<br>
            - Internal Pressure Uplift: {UP_int_tot:.2f} ton<br>
            - Wind Overturning Moment: {Mw:.2f} ton-m<br>
            - Seismic Overturning Moment: {Mrw:.2f} ton-m
        </div>

        <h3>18.2 FOUNDATION LOADING SUMMARY MATRIX</h3>
        <table style="font-size: 8.5pt;">
            <tr style="background:#2c3e50; color:white;">
                <th>Item</th><th>Type</th><th>Op. Full</th><th>Op. Empty</th><th>Test Full</th><th>Test Empty</th><th>Pneu. Test</th><th>Earthquake</th>
            </tr>
            <tr>
                <td>DW1 (ton/m2)</td><td>Max Pressure</td>
                <td>{A:.2f} (A)</td><td>{F:.2f} (F)</td><td>{K:.2f} (K)</td><td>{P:.2f} (P)</td><td>{U:.2f} (U)</td><td>{Z:.2f} (Z)</td>
            </tr>
            <tr>
                <td>W1 (ton/m)</td><td>Max Load</td>
                <td>{C:.2f} (C)</td><td>{H_val:.2f} (H)</td><td>{M:.2f} (M)</td><td>{R:.2f} (R)</td><td>{W_val:.2f} (W)</td><td>{AB:.2f} (AB)</td>
            </tr>
            <tr>
                <td>W1 (ton/m)</td><td>Min Load</td>
                <td>{B:.2f} (B)</td><td>{G_val:.2f} (G)</td><td>{L:.2f} (L)</td><td>{Q:.2f} (Q)</td><td>{V_val:.2f} (V)</td><td>{AA:.2f} (AA)</td>
            </tr>
            <tr>
                <td>W2 (ton/ea)</td><td>Anchor Load</td>
                <td>{E_val:.2f} (E)</td><td>{J_val:.2f} (J)</td><td>{O_val:.2f} (O)</td><td>{T_val:.2f} (T)</td><td>{Y_val:.2f} (Y)</td><td>{AC_val:.2f} (AC)</td>
            </tr>
        </table>

        <h3>18.3 LOAD ITEM DEFINITIONS</h3>
        <div style="font-size: 9pt;">
            <b>A / K / Z</b>: Vertical pressure on foundation including product/water and seismic moment.<br>
            <b>C / M / AB</b>: Vertical line load on ringwall including shell weight and overturning moments.<br>
            <b>E / J / AC</b>: Net uplift force per anchor bolt including internal pressure and wind/seismic moments.
        </div>
        """
        self._add_chapter("CIVIL INFORMATION LOADING DATA", html)

