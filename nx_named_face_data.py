import NXOpen
import NXOpen.UF
import math
import os


def main():
    the_session = NXOpen.Session.GetSession()
    the_uf_session = NXOpen.UF.UFSession.GetUFSession()
    work_part = the_session.Parts.Work
    lw = the_session.ListingWindow
    
    lw.Open()
    
    # Unit for centerline measurement
    unit_mm = work_part.UnitCollection.FindObject("MilliMeter")
    
    # Selection Setup
    resp, my_selected_objects = select_objects("Select multiple faces")
    
    if resp == NXOpen.Selection.Response.Ok:
        # First pass: collect all face data
        face_data_list = []
        
        for obj in my_selected_objects:
            if not isinstance(obj, NXOpen.Face):
                continue
            
            face = obj
            
            # Get original face name
            original_name = face.Name if face.Name else "No_Name"
            
            # 1. Get Face Physical Properties
            area, perimeter, rad_dia, cog, min_rad, area_err, anchor, is_approx = \
                the_session.Measurement.GetFaceProperties([face], 0.99, NXOpen.Measurement.AlternateFace.Radius, True)
            
            # 2. Get Centerline Properties
            pd_length, pvug_curves, start_pt, end_pt = the_session.Measurement.GetCenterlineProperties([face], unit_mm)
            
            # 3. Get Underlying Face Geometry Data
            f_type, f_pt, f_dir, bbox, f_radius, f_rad_data, norm_dir = the_uf_session.Modeling.AskFaceData(face.Tag)
            
            # 4. "Closed Cylinder" Logic
            close_cyl = "0"
            if f_type == 16: 
                expected_area = 2 * math.pi * f_radius * pd_length
                if round(area, 1) == round(expected_area, 1):
                    close_cyl = "1"
            
            # Store all data
            face_data_list.append({
                'original_name': original_name,
                'area': area,
                'f_radius': f_radius,
                'perimeter': perimeter,
                'cog': cog,
                'f_dir': f_dir,
                'f_type': f_type,
                'close_cyl': close_cyl
            })
        
        # Sort by name
        face_data_list.sort(key=lambda x: x['original_name'])
        
        # Count occurrences of each name
        name_counts = {}
        for data in face_data_list:
            name = data['original_name']
            name_counts[name] = name_counts.get(name, 0) + 1
        
        # Second pass: assign numbered names
        name_counter = {}
        output_rows = []
        
        # Header formatting
        header = "{:<25} {:<5} {:<25} {:<25} {:<25} {:<25} {:<25} {:<25} {:<25} {:<25} {:<25} {:<25} {:<25}".format(
            "#Label", " ", "Area", "Rad", "Peri", "X_0", "Y_0", "Z_0", "i", "j", "k", "Type", "ClosedCyl"
        )
        lw.WriteLine(header)
        output_rows.append(header)
        
        for data in face_data_list:
            original_name = data['original_name']
            
            # If name appears more than once, add numbering to ALL occurrences
            if name_counts[original_name] > 1:
                if original_name not in name_counter:
                    name_counter[original_name] = 1
                else:
                    name_counter[original_name] += 1
                display_name = f"{original_name}{name_counter[original_name]}"
            else:
                # Name appears only once, no numbering needed
                display_name = original_name
            
            # Format output row
            res_row = "{:<25} :: {:<25.4f} {:<25.4f} {:<25.4f} {:<25.4f} {:<25.4f} {:<25.4f} {:<25.4f} {:<25.4f} {:<25.4f} {:<25} {:<25}".format(
                display_name,
                data['area'], data['f_radius'], data['perimeter'], 
                data['cog'].X, data['cog'].Y, data['cog'].Z,
                data['f_dir'][0], data['f_dir'][1], data['f_dir'][2],
                data['f_type'], data['close_cyl']
            )
            
            lw.WriteLine(res_row)
            output_rows.append(res_row)
        
        # Write to text file
        output_path = write_output_file(output_rows, work_part)
        lw.WriteLine("\n" + "="*50)
        lw.WriteLine(f"Output saved to: {output_path}")

def write_output_file(rows, work_part):
    """Write the output to a text file in the same directory as the part"""
    try:
        # Get the part file path
        part_path = work_part.FullPath
        part_dir = os.path.dirname(part_path)
        part_name = os.path.splitext(os.path.basename(part_path))[0]
        
        # Create output filename
        output_filename = f"{part_name}_face_analysis.txt"
        output_path = os.path.join(part_dir, output_filename)
        
        # Write to file
        with open(output_path, 'w') as f:
            for row in rows:
                f.write(row + "\n")
        
        return output_path
    except Exception as e:
        # If part path is not available, save to temp directory
        import tempfile
        output_path = os.path.join(tempfile.gettempdir(), "face_analysis_output.txt")
        
        with open(output_path, 'w') as f:
            for row in rows:
                f.write(row + "\n")
        
        return output_path

def select_objects(prompt):
    """Utility to handle face selection UI"""
    the_ui = NXOpen.UI.GetUI()
    type_array = [NXOpen.Selection.SelectionType.Faces]
    resp, objects = the_ui.SelectionManager.SelectObjects(
        prompt, "Face Selection", 
        NXOpen.Selection.SelectionScope.AnyInAssembly, 
        False, type_array)
    return resp, objects

if __name__ == '__main__':
    main()