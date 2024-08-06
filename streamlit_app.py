import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from functions import *

# STREAMLIT APP
st.title("Bolt Resistance Calculator EN 1993-1-8")

col_1, col_2 = st.columns(2, vertical_alignment="top", gap="medium")

# SECTION 1 - MATERIAL
with col_1:
    st.header("MATERIAL")
    d = st.selectbox(label="Bolt diameter (d) [mm]",
                    options= diameters,
                    index=2)
    d0 = hole_diameter_params(d)
    st.caption("Hole diameter (d0) [mm]")
    st.markdown(d0)
    bolt_strength = st.selectbox(label="Bolt strength class",
                                options= bolt_strength_classes,
                                index=2)
    steel_strength = st.selectbox(label="Steel plate strength class",
                                options= steel_strength_classes,
                                index=0)
    t_plate = st.number_input("Plate thickness (t) [mm]", value=10, step=1)
    partial_factor = st.number_input("Partial factor ($\gamma_{M2}$)",
                                    value=1.25)

# SECTION 2 - GEOMETRY
with col_2:
    st.header("GEOMETRY")
    st.image('./static/bolt_distances.png')
    e1 = st.number_input("e1 - Edge distance, parallel with force direction",
                         step= 1,
                         min_value=int(np.ceil(min_distance_edge(d))),
                         help= "Minimum value: 1.2d0; Recommended value: 3.0d0")
    e2 = st.number_input("e2 - Edge distance, perpendicular to force direction",
                         step= 1,
                         min_value=int(np.ceil(min_distance_edge(d))),
                         help= "Minimum value: 1.2d0; Recommended value: 1.5d0")
    p1 = st.number_input("p1 - Center distance, parallel with force direction",
                         step= 1,
                         min_value=int(np.ceil(min_distance_p1(d))),
                         help= "Minimum value: 2.2d0; Recommended value: 3.75d0")
    p2 = st.number_input("p2 - Center distance, perpendicular to force direction",
                         step= 1,
                         min_value=int(np.ceil(min_distance_p2(d))),
                         help= "Minimum value: 2.4d0; Recommended value: 3.0d0")

    n_shear = st.number_input("Number of shear planes (n)", min_value=1, step=1)
    shear_thread = st.toggle("Shear plane in thread (True/False)", value=True)

# CALCULATION
bolt_props = bolt_properties(d, bolt_strength, diameters)
shear_res = bolt_shear_resistance(bolt_props, n_shear, shear_thread, partial_factor, bolt_strength)
bearing_res = bolt_bearing_resistance(d, bolt_props, e1, e2, p1, p2, t_plate, steel_strength, partial_factor)
tensile_res = bolt_tension_resistance(bolt_props, partial_factor)

results = [["Fv.Rd", shear_res], 
           ["Fb.Rd.1", bearing_res[0]],
           ["Fb.Rd.2", bearing_res[1]],
           ["Fb.Rd.3", bearing_res[2]],
           ["Fb.Rd.4", bearing_res[3]],
           ["Ft.Rd", tensile_res]]

df = pd.DataFrame(results,
                  index=["Shear resistance ",
                         "Bearing resistance (pos. 1 edge-edge)",
                         "Bearing resistance (pos. 2 edge-inner)",
                         "Bearing resistance (pos. 3 inner-edge)",
                         "Bearing resistance (pos. 4 inner-inner)",
                         "Tensile resistance"], 
                  columns=[" ", "Bolt resistances [kN]"])

st.header("RESULTS")
st.dataframe(df)

# COMMENTS
expander = st.expander("COMMENTS", expanded=False)
expander.markdown(
"""The bolts are **Category A** (bearing type) in shear, and **Category D** (non-preloaded) in tension.
The resistance values are calculated acc. to the formulas of EN 1993-1-8 Table 3.4. 
The side notes 1), 2), 3) are not considered.""")
expander.image('./static/bolt_categories.png')