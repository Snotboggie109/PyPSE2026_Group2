import streamlit as st

#Local application imports
from pages1.Utils1 import viewpoints_menu
from pages1.views import ppr_view
from pages1.views import additonal_views
from pages1.data.sample_data import sample_ppr_nodes, sample_ppr_edges

def show(engineering_nodes: dict, engineering_edges: list, sustainability_nodes: dict, sustainability_edges: list):
    """
    Displays a predefined PPR sample model.
    - Helps users understand the structure and relationships of a PPR model
    - Demonstrates application functionality without requiring file upload
    - Provides a safe, read-only environment (no modifications allowed)
    """
    # -------------------------------
    # Page header
    # -------------------------------
    st.header("📦 Explore Sample")
    st.markdown("A predefined example to understand the structure.")

    # -------------------------------
    # Viewpoint selection (PPR / Engineering / Sustainability)
    # -------------------------------
    selected_view = viewpoints_menu.handle("Explore Sample")
    if selected_view=="PPR View":
        ppr_view.show(nodes=sample_ppr_nodes, links=sample_ppr_edges,
                       engineering_nodes=engineering_nodes, engineering_edges=engineering_edges,
                       sustainability_nodes=sustainability_nodes, sustainability_edges=sustainability_edges, locked=True)        
    if selected_view=="Engineering View":
        additonal_views.show( ppr_nodes=sample_ppr_nodes,nodes= engineering_nodes,links=engineering_edges,selected_view=selected_view,locked=True)
    if selected_view=="Sustainability View":
         additonal_views.show( ppr_nodes=sample_ppr_nodes,nodes= sustainability_nodes,links=sustainability_edges,selected_view=selected_view,locked=True)

