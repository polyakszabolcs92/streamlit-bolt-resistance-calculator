import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from functions import *

# STREAMLIT APP
st.title("Bolt Resistance Calculator EN 1993-1-8")

# SECTION 1 - MATERIAL
st.header("MATERIAL PROPERTIES")
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
partial_factor = st.number_input("Partial factor ($\gamma_{M2}$)",
                                 value=1.25)

# SECTION 2 - GEOMETRY
st.divider()
st.header("GEOMETRY")
e1 = st.number_input("e1 - Edge distance, parallel with force direction (min. 1.2*d0)",
                     value="min",
                     step= 1,
                     min_value=int(np.ceil(min_distance_edge(d))),
                     help= "Recommended value: 3.0*d0")
e2 = st.number_input("e2 - Edge distance, perpendicular to force direction (min. 1.2*d0)",
                     value="min",
                     step= 1,
                     min_value=int(np.ceil(min_distance_edge(d))),
                     help= "Recommended value: 1.5*d0")
p1 = st.number_input("p1 - Center distance, parallel with force direction (min. 2.2*d0)",
                     value="min",
                     step= 1,
                     min_value=int(np.ceil(min_distance_p1(d))),
                     help= "Recommended value: 3.75*d0")
p2 = st.number_input("p2 - Center distance, perpendicular to force direction (min. 2.4*d0)",
                     value="min",
                     step= 1,
                     min_value=int(np.ceil(min_distance_p2(d))),
                     help= "Recommended value: 3.0*d0")

n_shear = st.number_input("Number of shear planes (n)", min_value=1, step=1)
shear_thread = st.toggle("Shear plane in thread (True/False)", value=True)
t_plate = st.number_input("Plate thickness (t) [mm]", value=10, step=1)


# CALCULATION
bolt_props = bolt_properties(d, bolt_strength, diameters)
shear_res = bolt_shear_resistance(bolt_props, n_shear, shear_thread, partial_factor, bolt_strength)
bearing_res = bolt_bearing_resistance(d, bolt_props, e1, e2, p1, p2, t_plate, steel_strength, partial_factor)
tensile_res = bolt_tension_resistance(bolt_props, partial_factor)

results = [[shear_res], 
           [bearing_res[0]],
           [bearing_res[1]],
           [bearing_res[2]],
           [bearing_res[3]],
           [tensile_res]]

df = pd.DataFrame(results,
                  index=["Fv.Rd - Shear resistance ",
                         "Fb.Rd.1 - Bearing resistance (pos. 1 edge-edge)",
                         "Fb.Rd.2 - Bearing resistance (pos. 2 edge-inner)",
                         "Fb.Rd.3 - Bearing resistance (pos. 3 inner-edge)",
                         "Fb.Rd.4 - Bearing resistance (pos. 4 inner-inner)",
                         "Ft.Rd - Tensile resistance"], 
                  columns=["Bolt resistances [kN]"])

st.divider()
st.header("RESULTS")
st.dataframe(df)