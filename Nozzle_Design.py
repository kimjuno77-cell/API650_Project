import math

class NozzleDesign:
    """
    Handles Nozzle Schedule and Basic Checks for API 650 Tank.
    Includes API 650 F.2.4 checking for roof nozzles under pressure > 2 kPa.
    """
    def __init__(self, nozzles_list=None):
        """
        :param nozzles_list: List of dicts defines nozzles.
                             Keys: Mark, Size (NPS), Service, Elevation, Remarks
        """
        self.nozzles = nozzles_list if nozzles_list else []
        self.results = {}
        
        # Standard Pipe ODs (mm) for NBS (Inch)
        self.pipe_od_map = {
            "2": 60.3, "3": 88.9, "4": 114.3, "6": 168.3,
            "8": 219.1, "10": 273.0, "12": 323.8, "14": 355.6,
            "16": 406.4, "18": 457.0, "20": 508.0, "24": 610.0,
            "30": 762.0, "36": 914.0, "Shell Manway 24": 610.0,
            "Roof Manway 24": 610.0
        }

    def get_standard_sizes(self):
        return list(self.pipe_od_map.keys())

    def process_nozzles(self):
        """
        Process list and adding missing details (OD, etc).
        """
        processed_list = []
        for i, nozzle in enumerate(self.nozzles):
            nps = str(nozzle.get('Size (NPS)', ''))
            mark = nozzle.get('Mark', f'N{i+1}')
            service = nozzle.get('Service', '')
            elev = nozzle.get('Elevation (m)', 0.0)
            
            # Lookup OD
            clean_nps = nps.replace('"', '').replace('in', '').strip()
            od = self.pipe_od_map.get(clean_nps, 0.0)
            
            # Extended Fields for Editor
            orient = nozzle.get('Orientation (deg)', 0)
            pipe_thk = nozzle.get('Pipe Thk (mm)', 0.0)
            repad = nozzle.get('Repad', False)
            
            processed_list.append({
                'Mark': mark,
                'Size': nps,
                'OD_mm': od,
                'Service': service,
                'Elevation': elev,
                'Orientation': orient,
                'Pipe_Thk_mm': pipe_thk,
                'Repad': repad,
                'Remarks': nozzle.get('Remarks', '')
            })
            
        self.results['nozzle_schedule'] = processed_list
        return processed_list

    def check_reinforcement(self, shell_courses, roof_t_used=6.0, roof_t_req=5.0, P_design_kPa=0.0):
        """
        Perform Reinforcement Area Check (API 650 5.7.2).
        Includes API 650 F.2.4 roof nozzle checks.
        """
        if not self.results.get('nozzle_schedule'):
            return []
            
        checked_list = []
        
        # Build cumulative height map for courses
        course_map = []
        cum_h = 0.0
        for c in shell_courses:
            h_course = c.get('Width', 0.0)
            t_used = c.get('t_used', 0.0)
            t_req = c.get('t_req', 0.0)
            if t_req == 0: t_req = t_used
            
            course_map.append({
                'bottom': cum_h,
                'top': cum_h + h_course,
                't_used': t_used,
                't_req': t_req,
                'name': c.get('Course', '')
            })
            cum_h += h_course
            
        for n in self.results['nozzle_schedule']:
            elev = n['Elevation']
            mark = n['Mark']
            od = n['OD_mm']
            repad = n['Repad']
            
            # Find Shell Course
            target_course = None
            for c in course_map:
                if c['bottom'] <= elev < c['top']:
                    target_course = c
                    break
            
            status = "N/A (Roof/Base?)"
            ratio = 0.0
            
            if target_course:
                # 1. Shell Nozzle Reinforcement (5.7.2)
                d = od
                t_s_used = target_course['t_used']
                t_s_req = target_course['t_req']
                
                A_req = d * t_s_req
                A1 = (t_s_used - t_s_req) * d
                if A1 < 0: A1 = 0
                
                A3 = 0.0
                if repad:
                    A3 = d * t_s_used
                    
                A_total = A1 + A3
                
                if A_req > 0:
                    ratio = A_total / A_req
                    status = "OK" if A_total >= A_req else "Reinforce Req"
                else:
                    status = "OK (Min Thk)"
                    
                n['Check_Course'] = target_course['name']
                n['t_used'] = t_s_used
                n['t_req'] = t_s_req
                n['A_req_mm2'] = A_req
                n['A_avail_mm2'] = A_total
                n['Status'] = status
                n['F24_Active'] = False
                n['F24_Warning'] = ""
                
            elif elev >= cum_h:
                # 2. Roof Nozzle Reinforcement Check (API 650 F.2.4)
                # If design pressure > 2 kPa, reinforcement check is MANDATORY per F.2.4 and 5.7
                d = od
                t_r_used = roof_t_used if roof_t_used else 6.0
                t_r_req = roof_t_req if roof_t_req else 5.0
                
                # F.2.4 mandatory reinforcement check if P > 2 kPa
                f24_active = P_design_kPa > 2.0
                
                # For roof plates, required area:
                A_req = d * t_r_req
                
                A1 = (t_r_used - t_r_req) * d
                if A1 < 0: A1 = 0
                
                A3 = 0.0
                if repad:
                    A3 = d * t_r_used
                
                A_total = A1 + A3
                
                if A_req > 0:
                    ratio = A_total / A_req
                    status = "OK" if A_total >= A_req else "Reinforce Req"
                else:
                    status = "OK (Min Thk)"
                
                f24_warn = ""
                if f24_active:
                    if status != "OK":
                        f24_warn = f"Design pressure ({P_design_kPa:.2f} kPa) > 2 kPa: Roof nozzle reinforcement is MANDATORY per F.2.4 (H_min = 5.0m assumed)."
                    else:
                        f24_warn = "Design pressure > 2 kPa: Roof nozzle reinforcement checked per F.2.4 and satisfied."
                
                n['Check_Course'] = "Roof Plate"
                n['t_used'] = t_r_used
                n['t_req'] = t_r_req
                n['A_req_mm2'] = A_req
                n['A_avail_mm2'] = A_total
                n['Status'] = status
                n['F24_Active'] = f24_active
                n['F24_Warning'] = f24_warn
                
            checked_list.append(n)
            
        self.results['nozzle_schedule'] = checked_list
        return checked_list
