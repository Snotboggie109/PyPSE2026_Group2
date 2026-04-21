import streamlit as st


#Local application imports
from pages1.Utils1 import viewpoints_menu
from pages1.views import ppr_view
from pages1.views import additonal_views


def show(engineering_nodes: dict, engineering_edges: list, sustainability_nodes: dict, sustainability_edges: list):
    """
    Handles interactive creation of a PPR model from scratch.

    Unlike the import module, this module:
    - Uses user-built nodes and edges stored in session state from scratch
    - Allows editing (unless workspace is locked)
    - Render selected viewpoint (PPR, Engineering, Sustainability)
    """   
    # -------------------------------
    # Retrieve built model from session
    # -------------------------------
    built_nodes= st.session_state.built_nodes
    built_edges= st.session_state.built_edges 

    # Ensure upload state exists (used for workspace conflict logic)
    if "upload" not in st.session_state:
        st.session_state.upload= None

    # -------------------------------
    # Page header
    # -------------------------------
    st.header("🛠️ Build PPR Model")
    st.markdown("Create a Process Product Resource model from scratch.")

    # -------------------------------
    # Workspace conflict handling
    # Prevent building if an imported model is active
    # -------------------------------
    if st.session_state.upload is not None:
        st.warning("""⚠️ **Workspace Already in Use**. A PPR model is currently active in the workspace. To build a new PPR model, please reset the workspace first.""")
        lock= True # Disable editing in views
    else:
        lock=False

    # -------------------------------
    # Viewpoint selection (PPR / Engineering / Sustainability)
    # -------------------------------
    selected_view = viewpoints_menu.handle("Build PPR Model")

    if selected_view=="PPR View":
        ppr_view.show(nodes=built_nodes, links=built_edges,
                       engineering_nodes=engineering_nodes, engineering_edges=engineering_edges,
                       sustainability_nodes=sustainability_nodes, sustainability_edges=sustainability_edges,locked=lock)        
    if selected_view=="Engineering View":
        additonal_views.show(ppr_nodes=built_nodes, nodes=engineering_nodes, links=engineering_edges, selected_view=selected_view, locked=lock)
    if selected_view=="Sustainability View":
        additonal_views.show(ppr_nodes=built_nodes, nodes=sustainability_nodes, links=sustainability_edges, selected_view=selected_view, locked=lock)