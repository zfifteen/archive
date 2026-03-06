import streamlit as st
import mpmath
import numpy as np
import plotly.graph_objects as go

def compute_helical_embedding(J, phi, dps, unfold_method):
    # set high-precision for zero computation
    mpmath.mp.dps = dps
    # fetch first J nontrivial Riemann zeta zeros (imag part positive)
    zeros = [mpmath.zetazero(i+1) for i in range(J)]
    imag_zeros = np.array([float(z.imag) for z in zeros])

    # apply unfolding
    if unfold_method == 'Standard':
        log_term = mpmath.log(imag_zeros / (2 * mpmath.pi * mpmath.e))
        unfolded = imag_zeros / (2 * mpmath.pi * log_term)
    elif unfold_method == 'Linear':
        unfolded = imag_zeros / (2 * mpmath.pi)
    else:  # Custom: simple log-scale
        unfolded = np.log(imag_zeros + 1)

    # helical coordinates
    theta = 2 * np.pi * unfolded / phi
    x = unfolded * np.cos(theta)
    y = unfolded * np.sin(theta)
    z = unfolded

    return x, y, z

def main():
    st.title("Interactive 3D Helical Embedding of Riemann Zeros")

    # Sidebar controls
    st.sidebar.header("Parameters")
    J = st.sidebar.slider("Number of zeros (J)", 10, 2000, 500, step=10)
    phi = st.sidebar.number_input("Phi (winding ratio)", value=(1 + 5**0.5)/2, format="%.4f")
    dps = st.sidebar.slider("mpmath precision (digits)", 10, 100, 50)
    unfold_method = st.sidebar.selectbox("Unfolding method", ["Standard", "Linear", "Custom"])
    point_size = st.sidebar.slider("Point size", 1, 20, 5)
    show_line = st.sidebar.checkbox("Connect with line", value=True)
    color_scatter = st.sidebar.color_picker("Scatter color", "#1f77b4")
    color_line = st.sidebar.color_picker("Line color", "#ff7f0e")
    elev = st.sidebar.slider("Camera elevation", 0, 90, 20)
    azim = st.sidebar.slider("Camera azimuth", -180, 180, 45)

    # Compute embedding
    with st.spinner("Computing embedding..."):
        x, y, z = compute_helical_embedding(J, phi, dps, unfold_method)

    # Build Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers",
        marker=dict(size=point_size, color=color_scatter),
        name="Zeros"
    ))
    if show_line:
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color=color_line, width=2),
            name="Helical Path"
        ))

    # Axes and camera
    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            camera_eye=dict(
                x=np.cos(np.deg2rad(azim)) * np.cos(np.deg2rad(elev)),
                y=np.sin(np.deg2rad(azim)) * np.cos(np.deg2rad(elev)),
                z=np.sin(np.deg2rad(elev))
            )
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
