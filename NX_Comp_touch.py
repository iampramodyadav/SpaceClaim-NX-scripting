import NXOpen
import NXOpen.Assemblies
import NXOpen.GeometricAnalysis
import os

def main():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    lw = theSession.ListingWindow
    
    lw.Open()
    lw.WriteLine("="*80)
    lw.WriteLine("Component Interference Analysis")
    lw.WriteLine("="*80)
    
    # Get all components in the assembly
    components = get_all_components(workPart)
    
    if len(components) < 2:
        lw.WriteLine("Error: Need at least 2 components to check interference")
        return
    
    lw.WriteLine(f"\nFound {len(components)} components in assembly\n")
    
    # Store results
    interference_results = []
    
    # Check interference between all component pairs
    total_checks = (len(components) * (len(components) - 1)) // 2
    check_count = 0
    
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            check_count += 1
            comp1 = components[i]
            comp2 = components[j]
            
            comp1_name = get_component_name(comp1)
            comp2_name = get_component_name(comp2)
            
            lw.WriteLine(f"Checking ({check_count}/{total_checks}): {comp1_name} vs {comp2_name}")
            
            # Check if components are touching
            is_touching, details = check_component_interference(theSession, workPart, comp1, comp2)
            
            result = {
                'component1': comp1_name,
                'component2': comp2_name,
                'touching': is_touching,
                'details': details
            }
            
            interference_results.append(result)
            
            if is_touching:
                lw.WriteLine(f"  >> TOUCHING: {details}")
            else:
                lw.WriteLine(f"  >> NOT TOUCHING")
            lw.WriteLine("")
    
    # Print summary
    print_summary(lw, interference_results)
    
    # Write results to file
    write_results_to_file(workPart, interference_results)
    
    lw.WriteLine("\nAnalysis complete!")

def get_component_name(component):
    """Get the display name of a component"""
    try:
        # Try DisplayName property first
        if hasattr(component, 'DisplayName'):
            return component.DisplayName
        # Fallback to Name property
        elif hasattr(component, 'Name'):
            return component.Name
        else:
            return str(component)
    except:
        return "Unknown Component"

def get_all_components(workPart):
    """Get all components in the assembly"""
    components = []
    root_component = workPart.ComponentAssembly.RootComponent
    
    if root_component is None:
        return components
    
    # Get all child components
    child_components = root_component.GetChildren()
    
    for comp in child_components:
        components.append(comp)
    
    return components

def get_component_bodies(component):
    """Get all solid bodies from a component"""
    bodies = []
    
    try:
        # Get the prototype part
        prototype = component.Prototype
        
        if prototype is None:
            return bodies
        
        # Get all bodies in the component
        body_collector = prototype.Bodies
        
        for body in body_collector:
            if body.IsSolidBody:
                bodies.append(body)
    
    except Exception as e:
        pass
    
    return bodies

def check_component_interference(theSession, workPart, comp1, comp2):
    """
    Check if any solid body from comp1 touches any solid body from comp2
    Returns: (is_touching: bool, details: str)
    """
    bodies1 = get_component_bodies(comp1)
    bodies2 = get_component_bodies(comp2)
    
    if not bodies1 or not bodies2:
        return False, "One or both components have no solid bodies"
    
    touching_pairs = []
    
    # Check each body pair
    for body1 in bodies1:
        for body2 in bodies2:
            try:
                markId = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Interference Check")
                
                # Create interference object
                simpleInterference = workPart.AnalysisManager.CreateSimpleInterferenceObject()
                
                # Set interference type to solid
                simpleInterference.InterferenceType = NXOpen.GeometricAnalysis.SimpleInterference.InterferenceMethod.InterferenceSolid
                simpleInterference.FaceInterferenceType = NXOpen.GeometricAnalysis.SimpleInterference.FaceInterferenceMethod.FirstPairOnly
                
                # Set bodies to check
                simpleInterference.FirstBody.Value = body1
                simpleInterference.SecondBody.Value = body2
                
                # Perform check (returns 1 if touching, 0 if not)
                result = simpleInterference.PerformCheck()
                
                # Clean up
                simpleInterference.Destroy()
                theSession.DeleteUndoMark(markId, None)
                
                if str(result) == str(1):
                    body1_name = body1.Name if hasattr(body1, 'Name') else str(body1)
                    body2_name = body2.Name if hasattr(body2, 'Name') else str(body2)
                    touching_pairs.append(f"{body1_name} <-> {body2_name}")
            
            except Exception as e:
                # Clean up on error
                try:
                    simpleInterference.Destroy()
                except:
                    pass
                continue
    
    if touching_pairs:
        details = f"Found {len(touching_pairs)} touching body pair(s)"
        return True, details
    else:
        return False, "No interference detected"

def print_summary(lw, results):
    """Print summary of results"""
    lw.WriteLine("\n" + "="*80)
    lw.WriteLine("SUMMARY OF RESULTS")
    lw.WriteLine("="*80)
    
    touching_count = sum(1 for r in results if r['touching'])
    total_count = len(results)
    
    lw.WriteLine(f"\nTotal component pairs checked: {total_count}")
    lw.WriteLine(f"Touching pairs: {touching_count}")
    lw.WriteLine(f"Non-touching pairs: {total_count - touching_count}")
    
    if touching_count > 0:
        lw.WriteLine("\n" + "-"*80)
        lw.WriteLine("TOUCHING COMPONENTS:")
        lw.WriteLine("-"*80)
        
        for result in results:
            if result['touching']:
                lw.WriteLine(f"  {result['component1']} <-> {result['component2']}")
                lw.WriteLine(f"    Details: {result['details']}")

def write_results_to_file(workPart, results):
    """Write results to a text file"""
    try:
        # Get the part file path
        part_path = workPart.FullPath
        part_dir = os.path.dirname(part_path)
        part_name = os.path.splitext(os.path.basename(part_path))[0]
        
        # Create output filename
        output_filename = f"{part_name}_interference_results.txt"
        output_path = os.path.join(part_dir, output_filename)
    except:
        # Fallback to temp directory
        import tempfile
        output_path = os.path.join(tempfile.gettempdir(), "interference_results.txt")
    
    with open(output_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("Component Interference Analysis Results\n")
        f.write("="*80 + "\n\n")
        
        # Write detailed results
        f.write("DETAILED RESULTS:\n")
        f.write("-"*80 + "\n")
        
        for result in results:
            status = "TOUCHING" if result['touching'] else "NOT TOUCHING"
            f.write(f"\n{result['component1']} <-> {result['component2']}\n")
            f.write(f"  Status: {status}\n")
            f.write(f"  Details: {result['details']}\n")
        
        # Write summary
        touching_count = sum(1 for r in results if r['touching'])
        total_count = len(results)
        
        f.write("\n" + "="*80 + "\n")
        f.write("SUMMARY:\n")
        f.write("="*80 + "\n")
        f.write(f"Total component pairs checked: {total_count}\n")
        f.write(f"Touching pairs: {touching_count}\n")
        f.write(f"Non-touching pairs: {total_count - touching_count}\n")
        
        if touching_count > 0:
            f.write("\n" + "-"*80 + "\n")
            f.write("TOUCHING COMPONENTS:\n")
            f.write("-"*80 + "\n")
            
            for result in results:
                if result['touching']:
                    f.write(f"  {result['component1']} <-> {result['component2']}\n")
    
    lw = NXOpen.Session.GetSession().ListingWindow
    lw.WriteLine(f"\nResults written to: {output_path}")
    return output_path

if __name__ == '__main__':
    main()