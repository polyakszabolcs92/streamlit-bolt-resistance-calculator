import numpy as np

diameters = [10, 12, 16, 20, 24, 27, 30, 33, 36, 39]
bolt_strength_classes = ['5.6', '5.8', '8.8', '10.9']
steel_strength_classes = ['S235', 'S275', 'S355', 'S460']

def hole_diameter_params(diameter):
    if diameter > 24:
        d0 = diameter+3
    elif diameter < 16:
        d0 = diameter+1
    else:
        d0 = diameter+2
    return d0

def min_distance_edge(diameter):
    d0 = hole_diameter_params(diameter)
    return 1.2 * d0

def min_distance_p1(diameter):
    return 2.2 * hole_diameter_params(diameter)

def min_distance_p2(diameter):
    return 2.4 * hole_diameter_params(diameter)

def bolt_properties(d, strength_class, diameter_array):
    """
    d: bolt diameter [int]
    strength_class [string]
    diameter_array: the list that contains the applicable bolt diameters
    """
    gross_areas = [78.5, 113., 201., 314., 452., 573., 707., 855., 1020., 1190.]
    stress_areas = [58., 84.3, 157., 245., 353., 459., 561., 694., 817., 976.]
        
    idx = diameter_array.index(d)
    
    # Hole diameter
    if d > 24:
        d0 = d+3
    elif d < 16:
        d0 = d+1
    else:
        d0 = d+2
    
    # Areas
    A = gross_areas[idx]
    As = stress_areas[idx]
    
    # Bolt strength
    strength_ult = strength_class.split('.')[0]
    fub = int(strength_ult) * 100
    
    return d0, A, As, fub


def steel_ultimate_strength(steel_strength, steel_strength_array):
    idx = steel_strength_array.index(steel_strength)
    f_ult = [360, 430, 510, 540]
    fu = f_ult[idx]
    return fu


def bolt_shear_resistance(props_array, n_shear, bool_shearplane, p_factor, strength_class):
    fub = props_array[3]
    
    if bool_shearplane == True:
        if (strength_class == '5.8') or (strength_class == '10.9'):
            av = 0.5
        else:
            av = 0.6
    else:
        av = 0.6
    
    if bool_shearplane == False:
        A = props_array[1]
    else:
        A = props_array[2]
    
    FvRd = round(n_shear * av * fub * A / p_factor /1000, 2)
    
    return FvRd


def bolt_bearing_resistance(d, props_array, e1, e2, p1, p2, t_plate, steel_strength, p_factor):
    fu = steel_ultimate_strength(steel_strength, steel_strength_classes)
    fub = props_array[3]
    d0 = props_array[0]
    
    # alfa.d factor (parallel with force)
    alfa_d_edge = np.min([e1/(3*d0), 1.0, fub/fu])      # szélső csavar
    alfa_d_inter = min(p1/(3*d0) - (1/4), 1.0, fub/fu)  # belső csavar
    
    # k1 factor (perpendicular to force)
    k1_edge = min(2.8*e2/d0 - 1.7, 2.5)     # szélső csavar
    k1_inter = min(1.4*p2/d0 - 1.7, 2.5)    # belső csavar
    
    # Bearing resistances
    FbRd_e_e = round(k1_edge * alfa_d_edge * fu * d * t_plate / p_factor /1000, 2)        # szélső - szélső
    FbRd_e_in = round(k1_edge * alfa_d_inter * fu * d * t_plate / p_factor /1000, 2)      # szélső - belső
    FbRd_in_e = round(k1_inter * alfa_d_edge * fu * d * t_plate / p_factor /1000, 2)      # belső - szélső
    FbRd_in_in = round(k1_inter * alfa_d_inter * fu * d * t_plate / p_factor /1000, 2)    # belső - belső
    
    return [FbRd_e_e, FbRd_e_in, FbRd_in_e, FbRd_in_in]


def bolt_tension_resistance(props_array, p_factor):
    As = props_array[2]
    fub = props_array[3]
    
    FtRd = round(0.9 * fub * As / p_factor /1000, 2)
    
    return FtRd