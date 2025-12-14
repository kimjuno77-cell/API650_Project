import math

class NozzleDesign:
    """
    Handles Nozzle Schedule and Basic Checks for API 650 Tank.
    """
    def __init__(self, nozzles_list=None):
        """
        :param nozzles_list: List of dicts defines nozzles.
                             Keys: Mark, NPS, Service, Elevation, Remarks
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
            # Strip " inch" or similar if present
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

    def check_reinforcement(self, shell_courses):
        """
        Perform Reinforcement Area Check (API 650 5.7.2).
        A_required = d * t_r (required shell thickness)
        A_available = A1 (Shell Excess) + A2 (nozzle excess) + A3 (Repad)
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
            t_req = c.get('t_req', 0.0) # Ensure this exists (ShellDesign output)
            if t_req == 0: t_req = t_used # Conservative fallback
            
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
                # API 650 5.7.2: Reinforcement
                # d = diameter of hole in shell (Assumed equal to OD_mm for set-through)
                d = od 
                
                t_s_used = target_course['t_used']
                t_s_req = target_course['t_req']
                
                # Required Area (A_req)
                # API 650 5.7.2.1: A_req = d * t_r
                # where t_r is the required shell thickness (calculated design thickness)
                A_req = d * t_s_req 
                
                # Available Area (A_total = A1 + A2 + A3 + A4)
                
                # A1: Excess Shell Thickness
                # Area available in the shell plate within vertical limits.
                # A1 = (t_used - t_req) * d (Simplified, ignoring vertical limit cap)
                A1 = (t_s_used - t_s_req) * d
                if A1 < 0: A1 = 0
                
                # A2: Excess Nozzle Neck Thickness
                # Requires nozzle neck thickness (Pipe_Thk_mm).
                # t_n_used = Pipe_Thk_mm
                # t_n_req = Pressure design + CA. Usually very small.
                # Assuming conservative A2 = 0 unless detailed data.
                tp = n.get('Pipe_Thk_mm', 0.0)
                A2 = 0.0
                if tp > 0:
                    # Very rough estimate: (tp - 0) * 4 * tp ? No.
                    # API 5.7.2.3: (2.5 * t_s) * (t_n - t_rn) * 2 sides
                    # Use safety factor: Ignore A2 for now to be conservative.
                    pass
                
                # A3: Reinforcing Pad (If applicable)
                A3 = 0.0
                if repad:
                    # Standard Pad Assumption:
                    # OD_pad = 2 * d
                    # Width_pad = (2d - d) / 2 = d/2 per side.
                    # Total Width = d.
                    # Thickness = t_s_used (Standard practice to match shell)
                    # A3 = Total_Width * t_pad = d * t_s_used
                    A3 = d * t_s_used 
                    
                # A4: Weld Metal (Ignored for preliminary)
                
                A_total = A1 + A2 + A3
                
                if A_req > 0:
                    ratio = A_total / A_req
                    
                    # Status Check
                    if A_total >= A_req:
                        status = "OK"
                    else:
                        status = "Reinforce Req"
                else:
                    status = "OK (Min Thk)"
                    
                n['Check_Course'] = target_course['name']
                n['A_req_mm2'] = A_req
                n['A_avail_mm2'] = A_total
                n['Status'] = status
                
            checked_list.append(n)
            
        self.results['nozzle_schedule'] = checked_list
        return checked_list
