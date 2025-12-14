
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

class HTMLReportGenerator:
    def __init__(self, template_folder='templates', template_name='report_template.html'):
        self.template_folder = template_folder
        self.template_name = template_name
        self.data_context = {}

    def set_project_info(self, project_name, designer_name):
        self.data_context['project_name'] = project_name
        self.data_context['designer_name'] = designer_name
        self.data_context['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    def set_design_data(self, D, H, G, P_design, CA, CA_roof, CA_bottom, shell_method):
        self.data_context.update({
            'D': D, 'H': H, 'G': G,
            'P_design': P_design,
            'CA': CA, 'CA_roof': CA_roof, 'CA_bottom': CA_bottom,
            'shell_method': shell_method
        })

    def set_results(self, W_shell_kg, W_roof_kg, net_uplift, anchor_status, 
                    shell_courses, roof_data, bottom_data, annular_data,
                    wind_data, seismic_data, roof_type, roof_slope,
                    struct_data=None, top_member_data=None, capacities_data=None, mawp_data=None, 
                    venting_data=None, wind_girder_data=None, nozzle_data=None, anchor_data=None,
                    shell_svg=None, nozzle_svg=None, efrt_data=None, standard_comparison=None, frangibility=None):
        self.data_context.update({
            'W_shell_kg': W_shell_kg,
            'W_roof_kg': W_roof_kg,
            'net_uplift': net_uplift,
            'anchor_status': anchor_status,
            'anchor_data': anchor_data or {}, # Detailed Results
            'shell_courses': shell_courses,
            'roof_data': roof_data,
            'bottom_data': bottom_data,
            'annular_data': annular_data,
            'wind_data': wind_data,
            'seismic_data': seismic_data,
            'roof_type': roof_type,
            'roof_slope': roof_slope,
            'struct_data': struct_data or {},
            'top_member_data': top_member_data or {},
            'capacities_data': capacities_data or {},
            'mawp_data': mawp_data or {},
            'venting_data': venting_data or {},
            'wind_girder_data': wind_girder_data or {},
            'nozzle_data': nozzle_data or {},
            'shell_svg': shell_svg or "",
            'nozzle_svg': nozzle_svg or "",
            'efrt_data': efrt_data or {},
            'standard_comparison': standard_comparison or {},
            'frangibility': frangibility or {}
        })

    def generate_html(self):
        """
        Renders the HTML and returns it as a string.
        """
        try:
            env = Environment(loader=FileSystemLoader(self.template_folder))
            template = env.get_template(self.template_name)
            html_out = template.render(self.data_context)
            return html_out
        except Exception as e:
            return f"Error generating HTML report: {e}"

    def save_html(self, output_path):
        html_content = self.generate_html()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return output_path
