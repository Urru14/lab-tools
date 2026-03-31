import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="XRD Plot App", layout="centered")

st.title("XRD Plot Generator")

# ===============================
# USER INPUT
# ===============================
num_files = st.number_input(
    "How many XRD files?",
    min_value=1,
    step=1
)

uploaded_files = st.file_uploader(
    "Upload XRD .xls/.xlsx files",
    type=["xls", "xlsx"],
    accept_multiple_files=True
)

use_custom_range = st.checkbox("Set custom X-axis range")

if use_custom_range:
    x_min = st.number_input("X min", value=0.0)
    x_max = st.number_input("X max", value=90.0)

offset = st.slider("Offset between plots", 0.1, 2.0, 0.5)

plot_button = st.button("Generate Plot")

# ===============================
# PROCESSING
# ===============================
if plot_button:

    if not uploaded_files:
        st.warning("Please upload files.")
        st.stop()

    if len(uploaded_files) != num_files:
        st.warning(f"Please upload exactly {num_files} files.")
        st.stop()

    fig, ax = plt.subplots(figsize=(8, 6))

    for i, file in enumerate(uploaded_files):

        try:
            df = pd.read_excel(file)

            # Assume first column = 2θ, second = intensity
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]

            # Normalize
            y = y / y.max()

            # Apply custom range
            if use_custom_range:
                mask = (x >= x_min) & (x <= x_max)
                x = x[mask]
                y = y[mask]

            # Clean filename (remove extension)
            filename = os.path.splitext(file.name)[0]

            # Plot
            ax.plot(x, y + i * offset, label=filename)

        except Exception as e:
            st.error(f"Error in file {file.name}: {e}")
            st.stop()

    # Labels
    ax.set_xlabel("2θ (degrees)")
    ax.set_ylabel("Normalized Intensity + Offset")
    ax.set_title("XRD Comparison")
    ax.legend(fontsize=8)

    plt.tight_layout()

    # Show plot
    st.pyplot(fig)

    # ===============================
    # DOWNLOAD BUTTON
    # ===============================
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button(
        label="Download Plot",
        data=buf.getvalue(),
        file_name="xrd_plot.png",
        mime="image/png"
    )
