"""
@Author:    Pramod Kumar Yadav
@email:     pkyadav01234@gmail.com
@Date:      March, 2024
@status:    testing
@python:    IronPython
@SpaceClaim: V232
@Overview: 
    This script automates the extraction of midsurfaces from solid bodies 
    within an Ansys SpaceClaim design. It offers two extraction methods:
        - **By Body:** Extracts a midsurface from each solid body based on a specified thickness range (inclusive).
        - **By Surface:** Creates a midsurface by selecting two opposing largest faces from a single solid body.
    The script also renames extracted midsurfaces based on a pattern derived from the component name.
@Usage:
    1. Modify the `min_thickness` and `max_thickness` variables according to your desired thickness range (in mm).
    2. Set `methode_by_body` to `True` to use the "By Body" method, or `False` to use the "By Surface" method.
    3. Run the script.
"""

import clr
clr.AddReference('System')
clr.AddReference('System.Windows.Forms')
import System.Windows.Forms as WinForms
from System.Drawing import Point as pt

# min_thickness = 0
# max_thickness = 10
extent_surf = True

methode_by_body = True

def main():
    min_thickness = int(inputBox("min_thickness", "Min thickness(mm):", "0"))
    max_thickness = int(inputBox("max_thickness", "Max thickness(mm):", "10"))
    
    extent_surf = int(inputBox("extent_surf:0/1", "Extend 1:Yes/0:No", "1"))
    methode_by_body = int(inputBox("methode_by_body:0/1", "1:Body 0:Surf", "1"))
    
    if extent_surf==1:
        extent_surf = True
    else:
        extent_surf = False
        
    if methode_by_body==1:
        methode_by_body = True
    else:
        methode_by_body = False   
    
    """
    - Retrieves the root component and its properties.
    - Iterates over all solid bodies.
    - For active and closed solid bodies:
        - Extracts a midsurface based on the selected method.
        - Renames all extracted midsurfaces.
        - Prints information about successfully and unsuccessfully extracted surfaces.
    """

    comp = GetRootPart()     
    RootNameComp = comp.GetName()
    RootCompCount = len(comp.Components)
    print('Number of comp in design', RootNameComp, " is " , RootCompCount)
    allSolid = comp.GetAllBodies()
    for soli in allSolid:
        not_active = soli.IsSuppressed
        is_solid=soli.GetMaster().Shape.IsClosed
        if not_active == False and is_solid == True:
            # print(soli.IsSuppressed)
            sel_i = Selection.Create(soli)
            if methode_by_body==True:
                print("Surface extraction by selecting body")
                extract_mid_body(sel_i, min_thickness, max_thickness, extent_surf)
            else:
                print("Surface extraction by selecting two surface")
                extract_mid_surf(soli)
     
    rename_midsurf(comp)
            
    print("Surface extracted for these solids")      
    for soli in allSolid:
        not_active = soli.IsSuppressed
        is_solid=soli.GetMaster().Shape.IsClosed
        parentCo = soli.Parent.GetName()
        if not_active == True and is_solid == True:
            name = soli.GetName()
            print(parentCo, "-->" ,name)       

    print("Surface not extracted for these solids change thicknes range or extract manuaaly")      
    for soli in allSolid:
        not_active = soli.IsSuppressed
        is_solid=soli.GetMaster().Shape.IsClosed
        parentCo = soli.Parent.GetName()
        if not_active == False and is_solid == True:
            name = soli.GetName()
            print(parentCo, "-->" ,name)
 
def rename_midsurf(comp):
    """
    - Iterates over all bodies.
    - For closed non-solid bodies (extracted midsurfaces):
        - Renames the body based on a pattern derived from the component name.
    """

    all_bodies=comp.GetAllBodies()
    for body in all_bodies:
        is_solid=body.GetMaster().Shape.IsClosed
        body_name=body.GetName()
        #print("Body name: %s is a solid body: %s"%(body_name,is_solid))
        if is_solid == False :
            # print(body_name)
            parentCo = body.Parent
            # print(parentCo.GetName()) 
            comp_name = parentCo.Parent.Parent.GetName()
            
            D_num = comp_name.split("_")[0]
            new_name = D_num
            body.SetName(new_name)
 
def extract_mid_body(iSelect, min_t=0, max_t=215, extend_opt = True):
    """
    - **min_t (float):** Minimum thickness for midsurface extraction (default: 0).
    - **max_t (float):** Maximum thickness for midsurface extraction (default: 215).
    - **extend_opt (bool):** Option to extend midsurfaces (default: True).
    
    - Extracts a midsurface from a given selection using the specified thickness range and extension option.
    - Returns 1 on success, 0 otherwise.
    """
    try:
        options = MidsurfaceOptions()
        options.CreationLocation = CreationLocation.SameComponent
        options.ExtendSurfaces = extend_opt
        
        command = Midsurface(options)
        command.AddFacePairsByRange(iSelect, MM(min_t), MM(max_t))
        result = command.Execute()
        
        if bool(result) == True:
            return 1
    except:
        return 0
        pass  
        
def extract_mid_surf(bdy):
    """
    - Extracts a midsurface by selecting the two largest opposing faces from a solid body.
    """
    face_area = {}
    for fac in bdy.Faces:
        area = fac.Area
        face_area[fac] = area
        
    sorted_by_valu = sorted(face_area.items(), key=lambda item: item[1],  reverse=True)

    flag = 0
    for f1 , surf_area1 in sorted_by_valu:
        if flag==1:
            # print("hi1")
            break
        for f2 , surf_area2 in sorted_by_valu:
            if flag ==1:
                # print("hi2")
                break
            if f1!=f2:
                try:
                    options = MidsurfaceOptions()
                    options.CreationLocation = CreationLocation.SameComponent
                    
                    command = Midsurface(options)
                    command.AddMatchingFacePairs(FaceSelection.Create(f1, f2))
                    result = command.Execute()
                    if bool(result) == True:
                        # print("hi3")
                        flag = 1
                        break
                except:
                    pass  


def inputBox(title, prompt, defaultValue):
    form = WinForms.Form()
    form.Text = title
    label = WinForms.Label()
    label.Text = prompt
    textBox = WinForms.TextBox()
    textBox.Text = defaultValue
    button = WinForms.Button()
    button.Text = "OK"
    label.Location = pt(10, 10)
    textBox.Location = pt(10, 40)
    button.Location = pt(150, 40)
    button.Click += lambda sender, args: form.Close()
    form.Controls.Add(label)
    form.Controls.Add(textBox)
    form.Controls.Add(button)
    form.ShowDialog()
    return textBox.Text
main()
