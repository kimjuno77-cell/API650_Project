
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
        self.generate_chapter_19_external_pressure()
        self.generate_chapter_20_nozzle_reinforcement()
        
        # 2. Assemble Final HTML
        return self._assemble_full_html()

    def _assemble_full_html(self):
        css = self._get_css()
        
        toc_html = "<div class='toc'><h2>TABLE OF CONTENTS</h2><div class='toc-container'><ul>"
        body_html = ""
        
        for ch in self.chapters:
            toc_html += f"""
            <li class='toc-item'>
                <span class='toc-title'>CHAPTER {ch['num']}. {ch['title']}</span>
                <span class='toc-dots'></span>
                <span class='toc-page'>Page {ch['num']*2 + 1}</span>
            </li>"""
            body_html += f"<div id='ch{ch['num']}' class='chapter'>"
            body_html += f"<h1 class='chapter-title'>CHAPTER {ch['num']}. {ch['title']}</h1>"
            body_html += "<hr class='chapter-divider'>"
            body_html += ch['content']
            body_html += "</div><div class='page-break'></div>"
            
        toc_html += "</ul></div></div><div class='page-break'></div>"
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API 650 Tank Design Report (Ver.2026)</title>
            <style>{css}</style>
        </head>
        <body>
            <div id="print-footer">Page <span class="page-num-content"></span></div>
            <div class='cover-page'>
                <h1>API 650 STORAGE TANK DESIGN CALCULATION</h1>
                <h2>PROJECT: HRSG AMMONIA STORAGE TANK (262-M-TK-101)</h2>
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
        
        .toc h2 { text-align: center; color: #2d3748; margin-bottom: 40px; font-weight: 700; font-size: 2.5rem; border-bottom: 3px solid #4ca1af; display: inline-block; padding-bottom: 10px; }
        .toc-container { width: 80%; margin: 0 auto; }
        .toc ul { list-style: none; padding: 0; }
        .toc-item { 
            display: flex; 
            align-items: baseline; 
            margin-bottom: 12px; 
            font-size: 1.05rem; 
            width: 100%;
        }
        .toc-title { flex-shrink: 0; font-weight: 600; color: #2d3748; }
        .toc-dots { flex-grow: 1; border-bottom: 2px dotted #cbd5e0; margin: 0 10px; height: 1em; min-width: 20px; }
        .toc-page { flex-shrink: 0; font-family: 'Roboto Mono', monospace; color: #4ca1af; font-weight: 700; min-width: 60px; text-align: right; }
        
        /* Print Footer */
        #print-footer {
            display: none;
            position: fixed;
            bottom: 20px;
            right: 40px;
            font-size: 10pt;
            color: #718096;
            font-family: 'Roboto Mono', monospace;
        }

        .chapter { padding: 60px 80px; page-break-after: always; }
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
        .toc { padding: 60px 80px; text-align: center; }

        @media print {
            body { padding: 0; }
            .chapter { padding: 40px; }
            .cover-page { background: white; color: black; border: 2px solid #2c3e50; height: 95vh; }
            .cover-table td { color: black; }
            .cover-page h1 { color: #2c3e50; }
            
            #print-footer { display: block; }
            .page-num-content::after { content: counter(page); }
            
            @page {
                margin: 2cm;
                @bottom-right {
                    content: "Page " counter(page);
                }
            }
        }
        """

    def generate_chapter_1_design_data(self):
        d = self.design
        p = self.project_info
        
        # Pressure conversions
        p_design_mmaq = d.get('P_design', 0)
        p_design_kpa = p_design_mmaq * 0.00980665
        p_ext_mmaq = d.get('P_external', 0)
        p_ext_kpa = p_ext_mmaq * 0.00980665
        
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
        </table>
        """
        
        design_table = f"""
        <table>
            <tr><th colspan="4" class="section-header">1.2 DESIGN PARAMETERS</th></tr>
            <tr>
                <td>Inside Diameter (ID):</td><td>{d.get('D',0):.3f} m</td>
                <td>Tank Height (H):</td><td>{d.get('H',0):.3f} m</td>
            </tr>
            <tr>
                <td>Design Specific Gravity:</td><td>{d.get('G',0):.3f}</td>
                <td>Max. Liquid Level (H.L.L):</td><td>{d.get('max_level',0):.3f} m</td>
            </tr>
            <tr>
                <td>Design Pressure (Int.):</td><td>{p_design_mmaq:.1f} mmH2O ({p_design_kpa:.3f} kPa)</td>
                <td>Design Pressure (Ext.):</td><td>{p_ext_mmaq:.1f} mmH2O ({p_ext_kpa:.3f} kPa)</td>
            </tr>
            <tr>
                <td>Design Temperature:</td><td>{d.get('design_temp',0):.1f} °C</td>
                <td>Design Metal Temp (MDMT):</td><td>{d.get('mdmt',0):.1f} °C</td>
            </tr>
            <tr>
                <td>Corrosion Allowance (Shell):</td><td>{d.get('CA',0):.1f} mm</td>
                <td>Shell Design Method:</td><td>{d.get('shell_method','-')}</td>
            </tr>
            <tr>
                <td>Corrosion Allowance (Roof):</td><td>{d.get('CA_roof',0):.1f} mm</td>
                <td>Corrosion Allowance (Bottom):</td><td>{d.get('CA_bottom',0):.1f} mm</td>
            </tr>
            <tr>
                <td>Material (Shell):</td><td>{d.get('mat_shell','-')}</td>
                <td>Joint Efficiency:</td><td>{d.get('joint_efficiency',1.0):.2f}</td>
            </tr>
            <tr>
                <td>Material (Roof):</td><td>{d.get('roof_material','-')}</td>
                <td>Material (Bottom):</td><td>{d.get('mat_bottom','-')}</td>
            </tr>
            <tr>
                <td>Material (Annular):</td><td>{d.get('mat_annular','-')}</td>
                <td>Roof Type:</td><td>{d.get('roof_type','-')}</td>
            </tr>
            <tr>
                <td colspan="4"><b>Applicable Annexes:</b>&nbsp;&nbsp;{', '.join(d.get('Applied_Annexes', [])) if d.get('Applied_Annexes') else '-'}</td>
            </tr>
        </table>
        """
        self._add_chapter("TANK DESIGN DATA", info_table + "<br>" + design_table)

    def generate_chapter_2_capacity(self):
        D = self.design.get('D', 0)
        H = self.design.get('H', 0)
        max_level = self.design.get('max_level', H)
        min_level = self.design.get('min_level', 0)
        
        geo_vol = math.pi * (D/2)**2 * H
        nom_vol = math.pi * (D/2)**2 * max_level
        net_vol = math.pi * (D/2)**2 * (max_level - min_level)

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
        
        # Determine Applied Annexes for Shell
        applied_logic = []
        if P_i > 2.5: applied_logic.append("Annex F (Internal Pressure) - Adjusted H_eff")
        if any('304' in str(c.get('Material','')) or '316' in str(c.get('Material','')) for c in courses):
            applied_logic.append("Annex S (Stainless Steel) - Specific Stresses & Min Thk")
        if self.design.get('design_temp', 40) > 93:
            applied_logic.append("Annex M (High Temperature) - Yield/Stress Derating")
        if method_name.lower() == 'annex_a':
            applied_logic.append("Annex A (Small Tanks) - Simplified Design Method")

        logic_html = ""
        if applied_logic:
            logic_html = "<div class='warning-box'><b>Applied Design Logic:</b><ul>"
            for lg in applied_logic:
                logic_html += f"<li>✅ {lg}</li>"
            logic_html += "</ul></div>"

        html = f"""
        <h3>3.1 INPUT SUMMARY</h3>
        {logic_html}
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
            t_req = c.get('t_req', 0)
            status_color = "#e53e3e" if t_use < t_req - 0.01 else "inherit"
            status_weight = "700" if t_use < t_req - 0.01 else "400"
            
            html += f"""<tr>
                <td>{c.get('Course','-')}</td><td>{c.get('Material','-')}</td>
                <td>{c.get('Sd',0):.0f}</td><td>{c.get('St',0):.0f}</td>
                <td>{c.get('td',0):.2f}</td><td>{c.get('tt',0):.2f}</td>
                <td>5</td><td style='color:{status_color}; font-weight:{status_weight};'><b>{t_use}</b></td>
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
                H_t = c.get('H_eff_t', H_d)
                Sd = c.get('Sd', 0)
                St = c.get('St', 0)
                td = c.get('td', 0)
                tt = c.get('tt', 0)
                
                # Recalculate H_eff for display matching PDF
                base_H = c.get('H_base', H_d - P_i / (9.8 * G) if G > 0 else H_d)
                H_eff_display = base_H + P_i / (9.8 * G) if G > 0 else H_d
                H_t_display  = base_H + 1.25 * P_i / (9.8 * 1.0)
                
                html += f"""
                <div class='calculation-block'>
                    <b>[Course {c.get('Course')}]</b><br>
                    - Effective Design Height, H<sub>eff</sub> = {base_H:.3f} + {P_i:.2f} / (9.8 * {G:.2f}) = <b>{H_eff_display:.3f} m</b><br>
                    - Required Thickness (Design), t<sub>d</sub> = [4.9 * D * (H_eff - 0.3) * G] / (Sd * E) + CA<br>
                    <code>t<sub>d</sub> = [4.9 * {D:.3f} * ({H_eff_display:.3f} - 0.3) * {G:.2f}] / ({Sd:.1f} * {E:.2f}) + {CA:.1f} = <b>{td:.2f} mm</b></code><br>
                    - Effective Test Height, H<sub>t</sub> = {base_H:.3f} + 1.25 * {P_i:.2f} / (9.8 * 1.0) = <b>{H_t_display:.3f} m</b><br>
                    - Required Thickness (Test), t<sub>t</sub> = [4.9 * D * (H_t - 0.3)] / (St * E)<br>
                    <code>t<sub>t</sub> = [4.9 * {D:.3f} * ({H_t_display:.3f} - 0.3)] / ({St:.1f} * {E:.2f}) = <b>{tt:.2f} mm</b></code><br>
                </div>
                """


        elif courses and is_vdm:
            html += "<b>API 650 5.6.4 Variable Design Point Method (VDM)</b><br>"
            html += """<div class='calculation-block'>
                <b>Notation:</b> H<sub>eff</sub> = Effective liquid height at course bottom,
                x = design point offset (0.61√(D·t) for upper courses),
                H_x = H<sub>eff</sub> - x<br><br>
            </div>"""
            for i, c in enumerate(courses):
                H_d    = c.get('H_eff_d', 0)
                Sd     = c.get('Sd', 0)
                St     = c.get('St', 0)
                td     = c.get('td', 0)
                tt     = c.get('tt', 0)
                t_use  = c.get('t_used', c.get('t_use', 0))
                t_prev = courses[i-1].get('t_used', td) if i > 0 else 0
                
                if i == 0:
                    # Bottom course: E.6.4.2
                    html += f"""<div class='calculation-block'>
                        <b>[Course {c.get('Course')} — Bottom Course, API 650 5.6.4.2]</b><br>
                        H<sub>eff</sub> = {H_d:.4f} m<br>
                        factor = 1.06 - (0.0696 * D / H<sub>eff</sub>) * √(H<sub>eff</sub> / S<sub>d</sub>)<br>
                        <code>t<sub>d</sub> = factor × [4.9 × D × H<sub>eff</sub> × G / (S<sub>d</sub> × E)] + CA = <b>{td:.3f} mm</b></code><br>
                        <code>t<sub>t</sub> = factor × [4.9 × D × H<sub>eff</sub> / S<sub>t</sub>] = <b>{tt:.3f} mm</b></code><br>
                        t<sub>min code</sub> = {c.get('t_req', max(td,tt)):.1f} mm &nbsp;→&nbsp; <b>t<sub>used</sub> = {t_use} mm</b>
                    </div>"""
                else:
                    # Upper course: E.6.4.3
                    x_d = 0.61 * math.sqrt(D * t_prev / 1000.0) if t_prev > 0 else 0
                    H_x_d = max(0, H_d - x_d)
                    html += f"""<div class='calculation-block'>
                        <b>[Course {c.get('Course')} — Upper Course, API 650 5.6.4.3]</b><br>
                        H<sub>eff</sub> = {H_d:.4f} m, &nbsp; t<sub>prev</sub> = {t_prev} mm<br>
                        x = 0.61 × √(D × t<sub>prev</sub>) = 0.61 × √({D:.3f} × {t_prev}/1000) = <b>{x_d:.4f} m</b><br>
                        H_x = H<sub>eff</sub> - x = {H_d:.4f} - {x_d:.4f} = <b>{H_x_d:.4f} m</b><br>
                        <code>t<sub>d</sub> = [4.9 × {D:.3f} × {H_x_d:.4f} × G] / (S<sub>d</sub> × E) + CA = <b>{td:.3f} mm</b></code><br>
                        <code>t<sub>t</sub> = [4.9 × {D:.3f} × {H_x_d:.4f}] / S<sub>t</sub> = <b>{tt:.3f} mm</b></code><br>
                        t<sub>min code</sub> = {c.get('t_req', max(td,tt)):.1f} mm &nbsp;→&nbsp; <b>t<sub>used</sub> = {t_use} mm</b>
                    </div>"""
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
        import Materials
        d = self.design
        design_temp = d.get('design_temp', 40)
        
        # Build component list with all relevant materials
        components = [
            ('Shell',   d.get('mat_shell', '-'),    d.get('CA', 0),       'd.get(\'joint_efficiency\',1.0)',  'API 650 Table 5-2a / Annex S'),
            ('Roof',    d.get('roof_material', '-'), d.get('CA_roof', 0),  '0.7',                              'API 650 5.10 / Annex S'),
            ('Bottom',  d.get('mat_bottom', '-'),    d.get('CA_bottom', 0),'0.7',                              'API 650 5.4'),
            ('Annular', d.get('mat_annular', '-'),   d.get('CA_bottom', 0),'0.7',                              'API 650 5.5 / Annex S'),
        ]
        
        joint_eff = d.get('joint_efficiency', 1.0)
        
        rows = ""
        for comp, mat, ca, _, code_ref in components:
            if mat == '-' or not mat:
                rows += f"<tr><td>{comp}</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>{ca:.1f}</td><td>-</td></tr>"
                continue
            try:
                props = Materials.get_material_properties(mat, design_temp)
                derated = Materials.get_derated_Sd(mat, design_temp) if design_temp > 40 else props.get('Sd', 0)
                fy  = props.get('Fy', '-')
                fu  = props.get('Fu', '-')
                sd_ambient = Materials.get_material_properties_base(mat).get('Sd', '-')
                st  = props.get('St', '-')
                sd_design = derated
                
                # Format status (derated vs ambient)
                sd_note = f"{sd_design:.0f}" if design_temp > 40 else f"{sd_ambient:.0f}"
                derated_flag = " ⚠️" if design_temp > 40 and isinstance(sd_design, (int,float)) and isinstance(sd_ambient, (int,float)) and sd_design < sd_ambient else ""
                
                rows += f"""<tr>
                    <td><b>{comp}</b></td>
                    <td>{mat}</td>
                    <td>{fy if isinstance(fy, str) else f'{fy:.0f}'}</td>
                    <td>{fu if isinstance(fu, str) else f'{fu:.0f}'}</td>
                    <td>{sd_ambient if isinstance(sd_ambient, str) else f'{sd_ambient:.0f}'}</td>
                    <td>{sd_note}{derated_flag}</td>
                    <td>{st if isinstance(st, str) else f'{st:.0f}'}</td>
                    <td>{ca:.1f}</td>
                </tr>"""
            except Exception as e:
                rows += f"<tr><td>{comp}</td><td>{mat}</td><td colspan='5'>Error: {e}</td><td>{ca:.1f}</td></tr>"
        
        # Determine applicable standard for shell
        mat_shell = d.get('mat_shell', '')
        is_ss = Materials.is_stainless_steel(mat_shell) if mat_shell else False
        annex_note = "Annex S (Stainless Steel) materials — Sd, St per Table S-1, min. thickness 5mm per Ann. S.3.1.1" if is_ss else "Carbon/Low-Alloy Steel — Sd, St per Table 5-2a"
        temp_note = f"<br><span style='color:#e53e3e;'>⚠️ Temperature Derating applied: Design Temp = {design_temp:.1f}°C > 40°C (Reference: API 650 Annex M)</span>" if design_temp > 40 else ""
        
        html = f"""
        <h3>4.1 MATERIAL PROPERTIES (at Design Temp)</h3>
        <div class='calculation-block'>
            <b>Applicable Code:</b> {annex_note}{temp_note}<br>
            <b>Design Temperature:</b> {design_temp:.1f} °C &nbsp;&nbsp; <b>Joint Efficiency (E):</b> {joint_eff:.2f}
        </div>
        <table>
            <tr>
                <th>Component</th>
                <th>Material</th>
                <th>Yield F<sub>y</sub> (MPa)</th>
                <th>Tensile F<sub>u</sub> (MPa)</th>
                <th>S<sub>d</sub> Ambient (MPa)</th>
                <th>S<sub>d</sub> @ Design T (MPa)</th>
                <th>S<sub>t</sub> (MPa)</th>
                <th>CA (mm)</th>
            </tr>
            {rows}
        </table>
        <p><i>
            S<sub>d</sub>: Allowable Design Stress (API 650 Table 5-2a / Table S-1)<br>
            S<sub>t</sub>: Allowable Hydrostatic Test Stress (API 650 Table 5-2a / Table S-1)<br>
            F<sub>y</sub>: Specified Minimum Yield Strength &nbsp;&nbsp; F<sub>u</sub>: Specified Minimum Tensile Strength<br>
            For Annex S (STS304/316): S<sub>d</sub> = 155 MPa, S<sub>t</sub> = 186 MPa, F<sub>y</sub> = 205 MPa (ASME SA-240)<br>
            Min. thickness: Shell/Roof 5mm per Annex S.3.1.1 / S.3.1.2, Bottom 5mm per API 650 5.4.1
        </i></p>

        <h3>4.2 MATERIAL SPECIFICATION SUMMARY</h3>
        <table>
            <tr><th>Component</th><th>Specification</th><th>Nominal t (mm)</th><th>Min. Required t (mm)</th><th>Code Reference</th></tr>
            <tr><td>Shell (Bottom Course)</td><td>{d.get('mat_shell','-')}</td>
                <td>{(self.results.get('shell_res') or {}).get('Shell Courses',[{}]) and (self.results.get('shell_res') or {}).get('Shell Courses',[{'t_used':0}])[0].get('t_used','-')}</td>
                <td>5 (Annex S)</td><td>API 650 Ann. S.3.1.1</td></tr>
            <tr><td>Roof Plate</td><td>{d.get('roof_material','-')}</td>
                <td>{(self.results.get('roof_res') or {}).get('Roof Plate',{}).get('Nominal Thickness','-')}</td>
                <td>5 (Annex S)</td><td>API 650 Ann. S.3.1.2</td></tr>
            <tr><td>Bottom Plate</td><td>{d.get('mat_bottom','-')}</td>
                <td>{(self.results.get('bottom_res') or {}).get('Bottom Plate',{}).get('Nominal Thickness','-')}</td>
                <td>6 (Gen.) / 5 (Ann. S)</td><td>API 650 5.4.1 / Ann. S.3.1.2</td></tr>
            <tr><td>Annular Plate</td><td>{d.get('mat_annular', d.get('mat_shell','-'))}</td>
                <td>-</td><td>As required by 5.5</td><td>API 650 5.5</td></tr>
        </table>
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
        <div class='calculation-block'>
            <b>API 650 5.4.1 Bottom Plate Requirements</b><br>
            All bottom plates shall have a corroded thickness of not less than 6 mm (0.236 in.).<br>
            <code>t_min = 6.0 + CA = 6.0 + {self.design.get('CA_bottom', 0):.1f} = {6.0 + self.design.get('CA_bottom', 0):.1f} mm</code><br>
            Provided Thickness: <b>{bott_res.get('Used Thk (mm)', 6)} mm</b>
        </div>
        
        <h3>5.2 BOTTOM PLATE WELDING (LAP JOINT)</h3>
        <div class='calculation-block'>
            <b>API 650 5.1.5.4.1 Lap-Welded Bottom Joints</b><br>
            Minimum Lap Width = max(5 * t_plate, 25 mm)<br>
            <code>Lap = max(5 * {bott_res.get('Used Thk (mm)', 6)}, 25) = {max(5 * bott_res.get('Used Thk (mm)', 6), 25):.0f} mm</code><br>
            Design Lap Width: <b>30 mm</b> (Standard Practice)
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
            <h3>6.1 ANNULAR PLATE REQUIREMENT (API 650 5.5)</h3>
            <div class='calculation-block'>
                <b>API 650 5.5.1 Annular Plate Requirement Check</b><br>
                Product Stress in 1st Shell Course:<br>
                <code>σ = (4.9 × D × (H - 0.3) × G) / t_provided</code><br>
                <code>σ = (4.9 × {D:.3f} × ({H_d:.3f} - 0.3) × {G:.3f}) / {t_prov:.2f} = <b>{stress:.1f} MPa</b></code><br><br>
                <b>API 650 Table 5-1: Minimum Annular Plate Thickness</b><br>
                <table style='width:auto; margin-left:20px;'>
                    <tr style='background:#4a5568;color:white;'>
                        <th>Condition (1st Course σ)</th><th>Min. t<sub>annular</sub> (mm)</th><th>Applicable?</th>
                    </tr>
                    <tr {'style="background:#c6f6d5;"' if stress <= 170 else ''}>
                        <td>σ ≤ 170 MPa</td><td>6.0 mm</td>
                        <td>{'✅ Governs' if stress <= 170 else '-'}</td>
                    </tr>
                    <tr {'style="background:#c6f6d5;"' if 170 < stress <= 190 else ''}>
                        <td>170 &lt; σ ≤ 190 MPa</td><td>8.0 mm</td>
                        <td>{'✅ Governs' if 170 < stress <= 190 else '-'}</td>
                    </tr>
                    <tr {'style="background:#c6f6d5;"' if 190 < stress <= 210 else ''}>
                        <td>190 &lt; σ ≤ 210 MPa</td><td>11.0 mm</td>
                        <td>{'✅ Governs' if 190 < stress <= 210 else '-'}</td>
                    </tr>
                    <tr {'style="background:#c6f6d5;"' if stress > 210 else ''}>
                        <td>σ &gt; 210 MPa</td><td>Special (per 5.5.3)</td>
                        <td>{'✅ Governs' if stress > 210 else '-'}</td>
                    </tr>
                </table><br>
                <b>Min. Annular Thickness Required:</b> {6.0 if stress <= 170 else (8.0 if stress <= 190 else (11.0 if stress <= 210 else 'Special'))} mm + CA
            </div>

            <h3>6.2 ANNULAR PLATE DIMENSIONS & PROJECTION</h3>
            <div class='calculation-block'>
                <b>API 650 5.5.2 Annular Plate Projection</b><br>
                The radial width of the annular plate shall not be less than 600 mm (24 in.).<br>
                Minimum Projection outside shell: <b>50 mm (2 in.)</b><br>
                Actual Width: <b>{ann_res.get('Width (mm)', 600):.0f} mm</b><br>
                Actual Projection: <b>{ann_res.get('Width (mm)', 600) - 200:.0f} mm</b> (Assumed default)
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
        
        if req == 'Yes':
            H1 = inter.get('H1_max', 0)
            t = inter.get('t_top', 0)
            V = self.design.get('V_wind', 45)
            V_mph = V * 3.6 / 1.609 
            
            html += f"""
            <div class='calculation-block'>
                <b>API 650 5.9.7.1 Intermediate Wind Girder Max Unstiffened Height (H1)</b><br>
                <code>H1 = 9.47 * t * sqrt((t / D)^3) * (190 / V)^2</code><br>
                <code>H1 = 9.47 * {t:.1f} * sqrt(({t:.1f} / {D:.3f})^3) * (190 / {V_mph:.1f})^2 = <b>{H1:.3f} m</b></code>
            </div>
            <table>
                <tr><td>Transformed Height (H_tr):</td><td>{inter.get('H_tr',0):.3f} m</td></tr>
                <tr><td>Max Unstiffened Height (H1):</td><td>{H1:.3f} m</td></tr>
                <tr><td>Number of Stiffeners:</td><td>{inter.get('Count',0)} EA</td></tr>
            </table>
            """
        else:
             html += f"<p>Intermediate Wind Girder is <b>Not Required</b> (Max unstiffened height {inter.get('H1_max',0):.2f}m exceeds transformed shell height {inter.get('H_tr',0):.2f}m).</p>"
            
        self._add_chapter("WIND GIRDER DESIGN", html)

    def generate_chapter_8_cone_roof(self):
        roof_res = self.results.get('roof_res', {})
        plate_res = roof_res.get('Roof Plate', {})
        lc_res = roof_res.get('Load Combinations', {})
        d = self.design
        D = d.get('D', 0)
        roof_type = d.get('roof_type', '')
        CA = d.get('CA_roof', 0)
        slope = d.get('roof_slope', 0.0625)
        theta_rad = math.atan(slope)
        sin_theta = math.sin(theta_rad)
        cos_theta = math.cos(theta_rad)
        
        # Pressures/Loads in kPa
        Pi = d.get('P_design', 0) * 0.00980665
        Pe = d.get('P_external', 0) * 0.00980665
        LL = d.get('live_load', 1.0)
        SL = d.get('snow_load', 0)
        DL_add = d.get('dead_load_add', 0)
        
        # Self Weight
        t_use = plate_res.get('Used Thk', 6.0)
        DL_plate = (t_use / 1000.0) * 7850.0 * 9.81 / 1000.0 # kPa
        DL_total = DL_add + DL_plate
        
        B_max = lc_res.get('Max_B_kPa', 1.2)
        
        html = f"""
        <h3>8.1 DESIGN LOAD SUMMARY (kPa)</h3>
        <table>
            <tr><th>Load Case</th><th>Formula / Description</th><th>Value (kPa)</th></tr>
            <tr><td>Dead Load (DL)</td><td>DL_add + (t_nom * rho_s * g) = {DL_add:.2f} + ({t_use}*7.85*0.00981)</td><td>{DL_total:.3f}</td></tr>
            <tr><td>Roof Live Load (Lr)</td><td>User Specified</td><td>{LL:.2f}</td></tr>
            <tr><td>Snow Load (S)</td><td>User Specified</td><td>{SL:.2f}</td></tr>
            <tr><td>Internal Pressure (Pi)</td><td>{d.get('P_design',0):.1f} mmH2O * 0.00981</td><td>{Pi:.3f}</td></tr>
            <tr><td>External Pressure (Pe)</td><td>{d.get('P_external',0):.1f} mmH2O * 0.00981</td><td>{Pe:.3f}</td></tr>
        </table>

        <h3>8.2 LOAD COMBINATIONS (API 650 5.2.2)</h3>
        <div class='calculation-block'>
            <b>LC e.1:</b> DL + (Lr or S) + 0.4*Pe = {DL_total:.3f} + {max(LL, SL):.2f} + 0.4*{Pe:.3f} = <b>{lc_res.get('LC_e1_Lr', 0):.3f} kPa</b><br>
            <b>LC e.2:</b> DL + Pe + 0.4*(Lr or S) = {DL_total:.3f} + {Pe:.3f} + 0.4*{max(LL, SL):.2f} = <b>{lc_res.get('LC_e2_Lr', 0):.3f} kPa</b><br>
            <b>Governing Load (B):</b> max(LC e.1, LC e.2) = <b>{B_max:.3f} kPa</b>
        </div>

        <h3>8.3 ROOF PLATE THICKNESS CALCULATION</h3>
        """
        
        if "Self-Supported" in roof_type:
            t_min_geom = D / (4.8 * sin_theta) if sin_theta > 0 else 0
            
            # F.6.1 Internal Pressure Check
            # t = P * R / (cos(theta) * Sd * E)
            Rt = D / (2 * sin_theta) if sin_theta > 0 else 0 # Radius of curvature approx
            Sd_roof = 155.0 # default for 304
            t_req_internal = (Pi * (D/2)) / (cos_theta * Sd_roof * 1.0) * 1000.0 / 1000.0 # Placeholder logic matching PDF
            
            # V.7.2.1 External Pressure (Buckling)
            # t_cone = 83 * D / sin(theta) * sqrt(Pr / (1.72 * E))
            E_mod = 193000.0 # MPa
            t_req_buckling = 83.0 * D / sin_theta * math.sqrt(B_max / (1.72 * E_mod)) if sin_theta > 0 else 0
            
            t_req_gov = max(t_min_geom, t_req_internal, t_req_buckling, 5.0) + CA
            
            html += f"""
            <div class='calculation-block'>
                <b>1) API 650 5.10.5.1 Minimum Thickness (Geometric):</b><br>
                <code>t_min = D / (4.8 * sin(theta)) + CA</code><br>
                <code>t_min = {D:.3f} / (4.8 * {sin_theta:.4f}) + {CA:.1f} = {t_min_geom+CA:.2f} mm</code><br><br>
                
                <b>2) API 650 Annex F.6.1 Internal Pressure:</b><br>
                <code>t_id = (Pi * R) / (cos(theta) * Sd * E) + CA</code><br>
                <code>t_id = ({Pi:.3f} * {D/2:.3f}) / ({cos_theta:.4f} * {Sd_roof} * 1.0) = {t_req_internal:.2f} mm</code><br><br>
                
                <b>3) API 650 Annex V.7.2.1 External Pressure (Buckling):</b><br>
                <code>t_cone = 83 * D / sin(theta) * sqrt(Pr / (1.72 * E)) + CA</code><br>
                <code>t_cone = 83 * {D:.3f} / {sin_theta:.4f} * sqrt({B_max:.3f} / (1.72 * {E_mod})) = {t_req_buckling:.2f} mm</code><br><br>
                
                <b>Result:</b> Required Thickness = max(t_min, t_id, t_cone, 5mm) = <b>{t_req_gov:.2f} mm</b><br>
                Provided Thickness = <b>{t_use:.2f} mm</b> &nbsp;&nbsp; <b>[ {plate_res.get('Status','-')} ]</b>
            </div>
            """
        else:
            html += f"""
            <div class='calculation-block'>
                <b>API 650 5.10.4 Supported Cone Roofs</b><br>
                Minimum Thickness: 5 mm (3/16 in.) + CA = <b>{5.0 + CA:.1f} mm</b><br>
                Provided Thickness: <b>{t_use:.2f} mm</b> &nbsp;&nbsp; <b>[ {plate_res.get('Status','-')} ]</b>
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
            </table>

            <h3>12.4 SEISMIC HOOP STRESS CHECK (API 650 E.6.1.4)</h3>
            
            """
            
            hoop = self.results.get('seismic_hoop_res', {})
            if hoop:
                html += f"""
                <div class="calculation-block">
                    <b>Hoop Stress Calculation:</b><br>
                    Stress, sigma_s = 4.9 * D * (H_eff - 0.3) * G / t + (4.9 * D * H_eff) / t * sqrt( (Ai*Wi)^2 + (Ac*Wc)^2 ) / W<br>
                    Calculated Stress: <b>{hoop.get('Stress_MPa', 0):.2f} MPa</b><br>
                    Allowable Stress: <b>{hoop.get('Allow_MPa', 0):.2f} MPa</b><br>
                    Status: <b class="{'result-pass' if hoop.get('Status') == 'OK' else 'result-fail'}">{hoop.get('Status','-')}</b>
                </div>
                """
            
            html += "<h3>12.4 SEISMIC HOOP STRESS CHECK (API 650 E.6.1.4)</h3>"
            
            hoop = self.results.get('seismic_hoop_res', {})
            if hoop:
                Ph   = hoop.get('Hydro_kPa', 0)
                Pdyn = hoop.get('Seismic_Add_kPa', 0)
                Ptot = Ph + Pdyn
                t_bot = self.results.get('shell_courses', [{}])[0].get('t_used', 0) if self.results.get('shell_courses') else 0
                D_ = self.design.get('D', 0)
                sigma = hoop.get('Stress_MPa', 0)
                allow = hoop.get('Allow_MPa', 0)
                s_cls = 'result-pass' if hoop.get('Status','') == 'OK' else 'result-fail'
                html += f"""
                <div class="calculation-block">
                    <b>E.6.1.4 Pressure Components at Bottom (y = 0):</b><br>
                    ① Hydrostatic: P<sub>h</sub> = γ × H<sub>liq</sub> = <b>{Ph:.3f} kPa</b><br>
                    ② Impulsive:  P<sub>i</sub> = Ai × γ × H<sub>liq</sub><br>
                    ③ Convective: P<sub>c</sub> = Ac × γ × H<sub>liq</sub><br>
                    ④ Vertical:   P<sub>av</sub> = (2/3)×SDS × γ × H<sub>liq</sub><br>
                    ⑤ Dynamic SRSS: P<sub>dyn</sub> = √(P<sub>i</sub>² + P<sub>c</sub>² + P<sub>av</sub>²) = <b>{Pdyn:.3f} kPa</b><br>
                    ⑥ Total: P<sub>total</sub> = P<sub>h</sub> + P<sub>dyn</sub> = {Ph:.3f} + {Pdyn:.3f} = <b>{Ptot:.3f} kPa</b><br><br>
                    σ<sub>hoop</sub> = P<sub>total</sub> × D / (2 × t) = {Ptot:.3f} × {D_:.3f} / (2 × {t_bot}/1000) = <b>{sigma:.2f} MPa</b><br>
                    Allowable = 1.333 × S<sub>d</sub> × E = <b>{allow:.2f} MPa</b><br>
                    → <b class="{s_cls}">{hoop.get('Status','-')}</b>
                </div>
                """

            html += "<h3>12.5 SEISMIC LONGITUDINAL COMPRESSION (API 650 E.6.2.2)</h3>"
            comp = self.results.get('seismic_comp_res', {})
            if comp:
                fc     = comp.get('fc_MPa', comp.get('Stress_MPa', 0))
                Fc     = comp.get('Fc_MPa', comp.get('Allow_MPa', 0))
                f_grav = comp.get('Gravity_Stress', 0)
                f_mom  = comp.get('Moment_Stress', 0)
                c_cls  = 'result-pass' if comp.get('Status','') == 'OK' else 'result-fail'
                html += f"""
                <div class="calculation-block">
                    <b>E.6.2.2.1 Compression Stress:</b><br>
                    σ<sub>c</sub> = [(W<sub>s</sub>+W<sub>r</sub>) / (π×D)] / t + [1.273×M<sub>s</sub> / D²] / t<br>
                    σ<sub>gravity</sub> = {f_grav:.3f} MPa &nbsp;|&nbsp; σ<sub>moment</sub> = {f_mom:.3f} MPa<br>
                    σ<sub>c</sub> = <b>{fc:.3f} MPa</b><br><br>
                    <b>E.6.2.2.3 Allowable F<sub>c</sub>:</b><br>
                    F<sub>c</sub> = min(0.4×F<sub>y</sub>, 0.25×E×t/D) = <b>{Fc:.3f} MPa</b><br>
                    → <b class="{c_cls}">{comp.get('Status','-')}</b>
                </div>
                """

            # E.7 Sloshing
            html += "<h3>12.6 SLOSHING WAVE HEIGHT & FREEBOARD (API 650 E.7)</h3>"
            sl = self.results.get('sloshing_res', {})
            if sl:
                dh  = sl.get('dh_m', 0)
                fb  = sl.get('Freeboard_m', 0)
                Tc_ = sl.get('Tc_s', 0)
                Ac_ = sl.get('Ac', 0)
                D_  = sl.get('D_m', self.design.get('D', 0))
                sl_cls = 'result-pass' if sl.get('Status','') == 'OK' else 'result-fail'
                html += f"""
                <div class="calculation-block">
                    <b>E.7.1 Sloshing Wave Height:</b><br>
                    T<sub>c</sub> = {Tc_:.2f} s &nbsp;|&nbsp; A<sub>c</sub> = {Ac_:.4f}<br>
                    d<sub>h</sub> = 0.5 × D × A<sub>c</sub> = 0.5 × {D_:.3f} × {Ac_:.4f} = <b>{dh:.3f} m</b><br><br>
                    <b>E.7.2 Freeboard Check:</b><br>
                    Available Freeboard = H<sub>shell</sub> − H<sub>liq</sub> = {sl.get('Tank_Height_m',0):.3f} − {sl.get('H_liq_m',0):.3f} = <b>{fb:.3f} m</b><br>
                    d<sub>h</sub> ({dh:.3f} m) {'≤' if dh<=fb else '>'} Freeboard ({fb:.3f} m)
                    → <b class="{sl_cls}">{sl.get('Status','-')}</b>
                    {'<br><span style="color:#e53e3e;">⚠️ ' + sl.get('Warning','') + '</span>' if sl.get('Warning') else ''}
                </div>
                """
            else:
                html += "<p>Sloshing check not performed (seismic not active).</p>"

            # E.8 Anchorage Ratio
            J = seismic.get('Anchorage_Ratio_J', 0)
            anc_stat = seismic.get('Anchorage_Status', '-')
            html += f"""
            <h3>12.7 ANCHORAGE RATIO J (API 650 E.6.2.1 / E.8)</h3>
            <div class="calculation-block">
                <b>E.6.2.1 Anchorage Ratio:</b><br>
                J = M<sub>rw</sub> / [D² × (w<sub>t</sub>×(1−0.4×A<sub>v</sub>) + w<sub>a</sub>)]<br>
                Where: w<sub>t</sub> = W<sub>shell</sub>/(π×D), w<sub>a</sub> = W<sub>roof</sub>/(π×D)<br>
                J = <b>{J:.3f}</b><br><br>
                <b>E.8 Interpretation:</b><br>
                J ≤ 0.785 → Self-Anchored (Stable)<br>
                0.785 < J ≤ 1.54 → Self-Anchored with Annular Plate Check<br>
                J > 1.54 → Mechanical Anchors Required<br>
                → <b>{anc_stat}</b>
            </div>
            """
            
            if graph:
                html += f'<h3>12.8 DESIGN SPECTRUM GRAPH</h3><img src="data:image/png;base64,{graph}" style="max-width:80%; margin: 20px auto; display:block; border: 1px solid #ddd;" />'

            
        self._add_chapter("SEISMIC DESIGN OF STORAGE TANK", html)

    def generate_chapter_13_anchor_bolt(self):
        anchor = self.results.get('anchor_res') or {}
        chair = self.results.get('anchor_chair_res') or {}
        
        status = anchor.get('Status', 'N/A')
        D = self.design.get('D', 0)
        N = anchor.get('Number of Bolts', 0)
        
        html = f"<h3>13.1 ANCHOR BOLT DESIGN SUMMARY</h3>"
        
        if status == 'Anchors Not Required' or N == 0:
             html += "<div class='warning-box'>Anchors are not required based on API 650 stability criteria.</div>"
        else:
             uplift_total = anchor.get('Net Uplift Force (kN)', 0)
             u_bolt = uplift_total / N if N > 0 else 0
             bolt_dia = anchor.get('Bolt Diameter (mm)', 0)
             
             # Uplift Cases
             cases = anchor.get('Uplift_Table', [])
             cases_rows = ""
             for c in cases:
                 cases_rows += f"<tr><td>{c['Case']}</td><td>{c['S_uplift']:.1f}</td><td>{c['W_resist']:.1f}</td><td><b>{c['Net_Uplift']:.1f}</b></td></tr>"
                 
             html += f"""
             <div class='calculation-block'>
                 <b>Uplift Force Evaluation (API 650)</b><br>
                 Uplift forces from Design Pressure, Wind, and Seismic are evaluated against Resisting Dead Loads.<br>
             </div>
             <table>
                 <tr><th colspan="4" class="section-header">Uplift Force Breakdown (kN)</th></tr>
                 <tr><th>Load Case</th><th>Total Uplift Load (Load)</th><th>Resisting Weight (Resist)</th><th>Net Uplift</th></tr>
                 {cases_rows}
             </table>
             <table>
                 <tr><th colspan="2" class="section-header">Anchor Bolt Parameters</th></tr>
                 <tr><td>Number of Bolts (N)</td><td>{N} EA</td></tr>
                 <tr><td>Bolt Diameter (d)</td><td><b>M{bolt_dia:.0f}</b></td></tr>
                 <tr><td>Total Net Uplift Force</td><td>{uplift_total:.1f} kN</td></tr>
                 <tr><td>Force per Bolt (U)</td><td>{u_bolt:.1f} kN</td></tr>
                 <tr><td>Required Bolt Area</td><td>{anchor.get('Required Bolt Area (mm2)', 0):.1f} mm²</td></tr>
             </table>
             """
             
        if chair and chair.get('Status') != 'N/A' and N > 0:
            html += "<h3>13.2 ANCHOR CHAIR DIMENSIONS</h3>"
            html += f"""
            <table>
                <tr><th>Description</th><th>Symbol</th><th>Value (mm)</th></tr>
                <tr><td>Top Plate Width</td><td>a</td><td>{chair.get('Top Plate Width (mm)', 0):.0f}</td></tr>
                <tr><td>Top Plate Length</td><td>b</td><td>{chair.get('Top Plate Width (mm)', 0):.0f}</td></tr>
                <tr><td>Top Plate Thickness</td><td>c</td><td>{chair.get('Top Plate Thk (mm)', 0):.0f}</td></tr>
                <tr><td>Chair Height</td><td>h</td><td>{chair.get('Chair Height (mm)', 0):.0f}</td></tr>
                <tr><td>Gusset Separation</td><td>g</td><td>{chair.get('Eccentricity (mm)', 0)*2:.0f}</td></tr>
                <tr><td>Gusset Thickness</td><td>j</td><td>13</td></tr>
            </table>
            """
        
        self._add_chapter("ANCHOR BOLT & ANCHOR CHAIR DESIGN", html)

        
    def generate_chapter_14_small_pressure(self):
        af = self.extended.get('annex_f') or {}
        max_P = af.get('Max Design Pressure P_max (kPa)', 0)
        P_fail = af.get('Failure Pressure P_fail (kPa)', 0)
        A_prov = af.get('Provided Area (mm2)', 0)
        A_req = af.get('Required Area (mm2)', 0)
        
        if not af:
             html = "<p>Annex F (Small Internal Pressure) checks not performed.</p>"
        else:
             D = self.design.get('D', 0)
             P_design_kPa = self.design.get('P_design', 0) * 0.00980665
             W = self.results.get('weights', {}).get('W_shell_kg', 0) * 9.81 + self.results.get('weights', {}).get('W_roof_kg', 0) * 9.81
             Fty = 200 # Assumed
             html = f"""
             <h3>14.1 ANNEX F CALCULATIONS (Small Internal Pressure)</h3>
             <div class='calculation-block'>
                 <b>API 650 F.4.1 Design Pressure Limits (Gravity)</b><br>
                 <code>P_max = W / (pi * D² / 4) / 1000  (kPa)</code><br>
                 <code>P_max = {W:.1f} / (pi * {D:.3f}² / 4) / 1000 = {max_P:.3f} kPa</code><br><br>
                 <b>API 650 F.5.1 Required Compression Area (A_req)</b><br>
                 <code>A_req = P_net * D² / (2.04 * Fy * tan(θ))</code><br>
                 <code>A_req = {P_design_kPa:.3f} * {D:.3f}² * 1000 / (2.04 * {Fty} * {math.tan(0.1667):.3f}) = {A_req:.1f} mm²</code><br><br>
                 <b>API 650 5.10.2.6 Calculated Failure Pressure</b><br>
                 <code>P_fail = 0.00127 * A * Fty / D² + 0.000122 * W_roof / D²  (kPa)</code><br>
                 <code>P_fail = 0.00127 * {A_prov:.1f} * {Fty} / {D:.3f}² + 0.000122 * {W:.1f} / {D:.3f}² = {P_fail:.3f} kPa</code>
             </div>
             <table>
                 <tr><th colspan="2" class="section-header">Annex F Design Verification</th></tr>
                 <tr><td>Design Internal Pressure (P)</td><td>{P_design_kPa:.3f} kPa</td></tr>
                 <tr><td>Max Design Pressure by Gravity (P_max)</td><td>{max_P:.3f} kPa</td></tr>
                 <tr><td>Calculated Failure Pressure (P_fail)</td><td>{P_fail:.3f} kPa</td></tr>
                 <tr><td>Top Angle Selected</td><td><b>{af.get('Top Angle', '-')}</b></td></tr>
                 <tr><td>Required Compression Area</td><td>{A_req:.1f} mm²</td></tr>
                 <tr><td>Provided Compression Area</td><td><b>{A_prov:.1f} mm²</b></td></tr>
                 <tr><td>Area Verification</td><td>{'<span class="result-pass">PASS</span>' if A_prov >= A_req else '<span class="result-fail">FAIL</span>'}</td></tr>
                 <tr><td>Frangibility Check</td><td>{af.get('Frangible?', '-')}</td></tr>
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

    def generate_chapter_19_external_pressure(self):
        v_res = self.results.get('annex_v_res', {})
        if not v_res:
            html = "<p>Annex V External Pressure check not applicable (Pe = 0).</p>"
        else:
            P_ext = v_res.get('P_ext_kPa', 0)
            Pe = v_res.get('Pe_kPa', 0)
            Pa = v_res.get('Pa_kPa', 0)
            N2 = v_res.get('N_sq', 0)
            t_min = v_res.get('t_min_mm', 0)
            
            html = f"""
            <h3>19.1 DESIGN CONDITIONS & MATERIAL</h3>
            <table>
                <tr><td>Design External Pressure (Pe)</td><td>{P_ext:.3f} kPa</td></tr>
                <tr><td>Minimum Shell Thickness used (t_min)</td><td>{t_min:.2f} mm</td></tr>
                <tr><td>Modulus of Elasticity (E)</td><td>193,000 MPa (Annex S)</td></tr>
            </table>

            <h3>19.2 UNSTIFFENED TANK BUCKLING (API 650 V.8.1)</h3>
            <div class='calculation-block'>
                <b>V.8.1.1 Elastic Buckling Pressure (Pe):</b><br>
                <code>Pe = [2.42 * E / (1 - mu^2)^0.75] * [(t/D)^2.5 / (L/D - 0.45(t/D)^0.5)]</code><br>
                <code>Pe = <b>{Pe:.3f} kPa</b></code><br><br>
                
                <b>V.8.1.2 Allowable External Pressure (Pa):</b><br>
                <code>Pa = Pe / 3.0 = {Pe:.3f} / 3 = <b>{Pa:.3f} kPa</b></code><br>
                Result: Pa ({Pa:.3f} kPa) {'&ge;' if Pa >= P_ext else '<'} Pe ({P_ext:.3f} kPa) &rarr; <b>{v_res.get('Status')}</b>
            </div>

            <h3>19.3 BOTTOM STIFFENER REGION (API 650 V.8.2.3)</h3>
            <div class='calculation-block'>
                <code>N² = (445 * D³) / (t * H²)</code><br>
                <code>N² = (445 * {v_res.get('D_m',0):.2f}³) / ({t_min} * {v_res.get('H_m',0):.2f}²) = <b>{N2:.1f}</b></code>
            </div>
            """
            
            if v_res.get('Status') == 'FAIL':
                html += f"""
                <h3>19.4 INTERMEDIATE STIFFENER REQUIREMENT</h3>
                <div class='calculation-block'>
                    Since Pa < Pe, intermediate stiffeners are required.<br>
                    Maximum Spacing (L_max): <b>{v_res.get('L_max_m', 0):.2f} m</b><br>
                    Required Number of Rings: <b>{v_res.get('Num_Rings', 0)} EA</b>
                </div>
                """
                
        self._add_chapter("EXTERNAL PRESSURE DESIGN (ANNEX V)", html)

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

    def generate_chapter_19_external_pressure(self):
        res = self.results.get('annex_v_res', {})
        if not res or res.get('Status') == 'Not Applicable':
            html = "<p>External pressure is not specified. Annex V is not applicable.</p>"
            self._add_chapter("ANNEX V (EXTERNAL PRESSURE)", html)
            return
            
        D = self.design.get('D', 0)
        H = self.design.get('H', 0)
        Pe = res.get('Elastic Buckling Pressure Pe (kPa)', 0)
        Pa = res.get('Allowable External Pressure Pa (kPa)', 0)
        P_ext = res.get('Design External Pressure (kPa)', 0)
        
        html = f"""
        <h3>19.1 EXTERNAL PRESSURE DESIGN (ANNEX V)</h3>
        <div class='calculation-block'>
            <b>API 650 V.8.1.1 Elastic Buckling Pressure (P<sub>e</sub>)</b><br>
            <code>Pe = [2.42 * E / (1 - &mu;&sup2;)&deg;⁷⁵] * [(t/D)&sup2;.⁵ / (L/D - 0.45&radic;(t/D))]</code><br>
            <code>Pe = {Pe:.3f} kPa</code><br><br>
            <b>API 650 V.8.1.2 Allowable External Pressure (P<sub>a</sub>)</b><br>
            <code>Pa = Pe / 3 = {Pa:.3f} kPa</code><br><br>
            <table>
                <tr><td>Design External Pressure:</td><td>{P_ext:.3f} kPa</td></tr>
                <tr><td>Allowable Pressure (Pa):</td><td>{Pa:.3f} kPa</td></tr>
                <tr><td>Status:</td><td><b>{res.get('Status','-')}</b></td></tr>
            </table>
        </div>

        <h3>19.2 BOTTOM STIFFENER REGION (V.8.2.3)</h3>
        <div class='calculation-block'>
            <b>API 650 V.8.2.3 End Stiffener Factor N²:</b><br>
            <code>N² = (445 × D³) / (t × H²)</code><br>
            <code>N² = (445 × {D:.3f}³) / ({res.get('t_min_mm',0):.1f} × {H:.3f}²) = <b>{res.get('N_sq',0):.2f}</b></code><br>
            <i>Note: N² ≤ 6 → Bottom stiffener required</i>
        </div>
        """

        if res.get('Status') == 'FAIL':
            L_max = res.get('L_max_m', 0)
            N_rings = res.get('Num_Rings', 0)
            html += f"""
            <h3>19.3 INTERMEDIATE STIFFENER RINGS REQUIRED (V.8.1.2 FAIL)</h3>
            <div class='calculation-block'>
                <b>Since Pa &lt; P_ext, intermediate stiffener rings are required.</b><br><br>
                Maximum Ring Spacing (L_max):<br>
                <code>L_max = D × [(coeff × (t/D)^2.5 / (3 × P_ext)) + 0.45 × √(t/D)]</code><br>
                <code>L_max = <b>{L_max:.3f} m</b></code><br><br>
                Required Number of Rings = ⌈H / L_max⌉ − 1 = <b>{N_rings} EA</b><br>
                Minimum Ring Size: Per API 650 V.9, select a ring with Z ≥ required modulus.
            </div>
            """
        else:
            html += "<div class='calculation-block'>Unstiffened shell is adequate. <b>No intermediate rings required.</b></div>"
        
        self._add_chapter("ANNEX V (EXTERNAL PRESSURE)", html)

    def generate_chapter_20_nozzle_reinforcement(self):
        """
        API 650 5.7.2 Nozzle Reinforcement Area Check.
        """
        nozzles = self.results.get('nozzle_res', [])
        if not nozzles:
            nozzles = (self.results.get('nozzle_schedule', []) or
                       (self.results.get('nozzle_data') or {}).get('nozzle_schedule', []))
        
        if not nozzles:
            self._add_chapter("NOZZLE REINFORCEMENT (5.7.2)",
                              "<p>No nozzle data provided or not applicable.</p>")
            return

        html = f"""
        <h3>20.1 NOZZLE REINFORCEMENT BASIS</h3>
        <div class='calculation-block'>
            <b>API 650 5.7.2 Reinforcement Area Method</b><br>
            Required Area: A<sub>req</sub> = d × t<sub>r</sub> &nbsp;(d = nozzle hole diameter, t<sub>r</sub> = required shell thickness)<br>
            Available Area: A<sub>avail</sub> = A<sub>1</sub> (shell excess) + A<sub>2</sub> (nozzle excess) + A<sub>3</sub> (repad)<br>
            Criterion: A<sub>avail</sub> ≥ A<sub>req</sub>
        </div>
        <h3>20.2 NOZZLE SCHEDULE & REINFORCEMENT CHECK</h3>
        <table>
            <tr style='background:#2d3748;color:white;'>
                <th>Mark</th><th>Service</th><th>Size (NPS)</th><th>OD (mm)</th>
                <th>Elev (m)</th><th>Course</th><th>t<sub>r</sub> (mm)</th>
                <th>t<sub>used</sub> (mm)</th><th>A<sub>req</sub> (mm²)</th>
                <th>A<sub>1</sub> (mm²)</th><th>A<sub>3</sub> (Repad)</th>
                <th>A<sub>avail</sub> (mm²)</th><th>Ratio</th><th>Status</th>
            </tr>
        """
        
        for n in nozzles:
            mark  = n.get('Mark', '-')
            svc   = n.get('Service', '-')
            sz    = n.get('Size', n.get('Size (NPS)', '-'))
            od    = n.get('OD_mm', 0)
            elev  = n.get('Elevation', n.get('Elevation (m)', 0))
            course= n.get('Check_Course', '-')
            t_req = n.get('t_req', 0)   # Required shell thickness (from calculation)
            t_used= n.get('t_used', 0)  # Used shell thickness
            A_req = n.get('A_req_mm2', od * t_req if t_req > 0 else 0)
            A_av  = n.get('A_avail_mm2', 0)
            A1    = max(0, (t_used - t_req) * od) if (t_used > 0 and t_req > 0 and od > 0) else 0
            A3    = A_av - A1  # Approximate repad contribution
            ratio = A_av / A_req if A_req > 0 else 999
            st    = n.get('Status', 'OK' if ratio >= 1.0 else 'FAIL')
            cls   = 'result-pass' if st == 'OK' else 'result-fail'
            html += f"""
            <tr>
                <td><b>{mark}</b></td><td>{svc}</td><td>{sz}"</td><td>{od:.1f}</td>
                <td>{elev:.2f}</td><td>{course}</td>
                <td>{t_req:.2f}</td><td>{t_used}</td>
                <td>{A_req:.0f}</td><td>{A1:.0f}</td><td>{max(0,A3):.0f}</td>
                <td><b>{A_av:.0f}</b></td><td>{ratio:.2f}</td>
                <td class='{cls}'><b>{st}</b></td>
            </tr>"""
        
        html += "</table>"
        self._add_chapter("NOZZLE REINFORCEMENT (5.7.2)", html)
