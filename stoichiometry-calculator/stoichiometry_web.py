import streamlit as st
import re
import pandas as pd


# -------------------------------
# Atomic weights dictionary
# -------------------------------
atomic_weights = {
    "H": 1.008, "He": 4.0026,
    "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180,
    "Na": 22.989, "Mg": 24.305, "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948,
    "K": 39.098, "Ca": 40.078, "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996, "Mn": 54.938,
    "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971, "Br": 79.904, "Kr": 83.798,
    "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.224, "Nb": 92.906, "Mo": 95.95,
    "Tc": 98, "Ru": 101.07, "Rh": 102.91, "Pd": 106.42, "Ag": 107.87, "Cd": 112.41,
    "In": 114.82, "Sn": 118.71, "Sb": 121.76, "Te": 127.60, "I": 126.90, "Xe": 131.29,
    "Cs": 132.91, "Ba": 137.33, "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24,
    "Pm": 145, "Sm": 150.36, "Eu": 151.96, "Gd": 157.25, "Tb": 158.93, "Dy": 162.50,
    "Ho": 164.93, "Er": 167.26, "Tm": 168.93, "Yb": 173.05, "Lu": 174.97,
    "Hf": 178.49, "Ta": 180.95, "W": 183.84, "Re": 186.21, "Os": 190.23, "Ir": 192.22,
    "Pt": 195.08, "Au": 196.97, "Hg": 200.59,
    "Tl": 204.38, "Pb": 207.2, "Bi": 208.98, "Po": 209, "At": 210, "Rn": 222,
    "Fr": 223, "Ra": 226, "Ac": 227, "Th": 232.04, "Pa": 231.04, "U": 238.03,
    "Np": 237, "Pu": 244, "Am": 243, "Cm": 247, "Bk": 247, "Cf": 251,
    "Es": 252, "Fm": 257, "Md": 258, "No": 259, "Lr": 266,
    "Rf": 267, "Db": 268, "Sg": 269, "Bh": 270, "Hs": 269, "Mt": 278,
    "Ds": 281, "Rg": 282, "Cn": 285, "Nh": 286, "Fl": 289, "Mc": 290,
    "Lv": 293, "Ts": 294, "Og": 294
}


# -------------------------------
# Parse formula
# -------------------------------
def parse_formula(formula):
    elements = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
    composition = {}

    for element, count in elements:
        if count == "":
            count = 1
        else:
            count = float(count)

        composition[element] = composition.get(element, 0) + count

    return composition


# -------------------------------
# Molecular weight
# -------------------------------
def molecular_weight(formula):
    comp = parse_formula(formula)
    mw = 0

    for element, count in comp.items():
        if element not in atomic_weights:
            st.error(f"Atomic weight for {element} not found.")
            return None
        mw += atomic_weights[element] * count

    return mw


# -------------------------------
# UI
# -------------------------------

st.title("Stoichiometric Precursor Calculator")

product_formula = st.text_input("Final Product Formula")

desired_grams = st.number_input("Desired grams of final product", min_value=0.0)

num_precursors = st.number_input("Number of precursors", min_value=1, step=1)

precursors = []

for i in range(int(num_precursors)):
    st.subheader(f"Precursor {i+1}")
    precursor_formula = st.text_input(f"Precursor {i+1} Formula", key=f"pf{i}")
    supplied_element = st.text_input(f"Supplied Element", key=f"el{i}")
    precursors.append((precursor_formula, supplied_element))


if st.button("Calculate"):

    product_comp = parse_formula(product_formula)
    product_mw = molecular_weight(product_formula)

    if product_mw is not None:

        st.write(f"### Molecular Weight: {round(product_mw,6)} g/mol")

        results = []

        for precursor_formula, supplied_element in precursors:

            precursor_comp = parse_formula(precursor_formula)
            precursor_mw = molecular_weight(precursor_formula)

            if supplied_element not in precursor_comp:
                st.error(f"{supplied_element} not found in {precursor_formula}")
                continue

            atoms_in_precursor = precursor_comp[supplied_element]
            required_atoms = product_comp[supplied_element]

            grams_required = (precursor_mw / product_mw) * (required_atoms / atoms_in_precursor)

            results.append({
                "Precursor": precursor_formula,
                "Required for 1 g (g)": round(grams_required, 8),
                f"Required for {desired_grams} g (g)": round(grams_required * desired_grams, 8)
            })

        df = pd.DataFrame(results)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Results as CSV",
            csv,
            "stoichiometry_results.csv",
            "text/csv"
        )

