import streamlit as st
import xml.etree.ElementTree as et
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Layout
from yfiles_graphs_for_streamlit import NodeStyle, NodeShape
import xml.etree.ElementTree as ET
import networkx as nx
from streamlit_option_menu import option_menu

#Local application imports
from pages1 import import_model, build_ppr, explore_sample, help_docs

# Sample datasets used in "Explore Sample" view
from pages1.data.sample_data import  sample_eng_nodes, sample_eng_edges, sample_sus_nodes, sample_sus_edges

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(page_title="Product-Process-Resource (PPR) Visualizer", page_icon="⚙️",layout="wide",initial_sidebar_state="collapsed")
st.title("⚙️ Product-Process-Resource (PPR) Visualizer")


# -------------------------------
# Sidebar navigation options
# -------------------------------
sidebar_menu = ["Import Model", "Build PPR Model", "Explore Sample","Help and Docs"]

# -------------------------------
# Session State Initialization
# Ensures persistence across reruns
# -------------------------------

# Track current active page
if "main_menu" not in st.session_state:
    st.session_state.main_menu = "Import Model"


# Dedicated Session states for viewpoints (Engineering + Sustainability) for imported model data
if "engineering_nodes" not in st.session_state:
    st.session_state.engineering_nodes = {}  # Store a copy of the elements dictionary in session state
if "engineering_edges" not in st.session_state:
    st.session_state.engineering_edges = [] # Store a copy of the engineering link list in session state
if "sustainability_nodes" not in st.session_state:
    st.session_state.sustainability_nodes = {}
if "sustainability_edges" not in st.session_state:
    st.session_state.sustainability_edges = []

# Dedicated Session states for PPR data (created in the app from scratch)
if "built_nodes" not in st.session_state:
    st.session_state.built_nodes = {}  # Store a copy of the built nodes dictionary in session state
if "built_edges" not in st.session_state:
    st.session_state.built_edges = []  # Store a copy of the built edges list in session state

# Dedicated Session states for viewpoints (Engineering + Sustainability) for built model data
if "built_sustainability_nodes" not in st.session_state:
    st.session_state.built_sustainability_nodes = {}
if "built_sustainability_edges" not in st.session_state:
    st.session_state.built_sustainability_edges = []
if "built_engineering_nodes" not in st.session_state:
    st.session_state.built_engineering_nodes = {}
if "built_engineering_edges" not in st.session_state:
    st.session_state.built_engineering_edges = []


# -------------------------------
# Local references (for readability)
# -------------------------------
engineering_nodes= st.session_state.engineering_nodes
engineering_edges= st.session_state.engineering_edges 

sustainability_nodes= st.session_state.sustainability_nodes
sustainability_edges= st.session_state.sustainability_edges

built_engineering_nodes=st.session_state.built_engineering_nodes 
built_engineering_edges= st.session_state.built_engineering_edges

built_sustainability_nodes= st.session_state.built_sustainability_nodes
built_sustainability_edges=st.session_state.built_sustainability_edges

# -------------------------------
# Maintain selected menu state
# -------------------------------
current = st.session_state.get("main_menu")
current_index = sidebar_menu.index(current)

# -------------------------------
# Sidebar UI
# -------------------------------

with st.sidebar:
    selected_sidebar=option_menu("Workspace",
                     sidebar_menu,
                     icons=["upload","diagram-3","box-seam","question-circle"],
                     menu_icon="grid",
                     default_index=current_index,
                     orientation= "vertical",
                     key="main_menu")

    # ---------------------------
    # Workspace Reset Functionality
    # Clears session while preserving navigation state
    # ---------------------------

    if st.button("Reset Workspace", key="reset_button"):
        @st.dialog("Reset Workspace")
        def reset_workspace():
            st.write("Are you sure you want to reset everything?")

            if st.button("OK"):

                a= st.session_state.main_menu
                if "view_of" in st.session_state:
                    b= st.session_state.view_of
                st.session_state.clear()
                st.session_state.main_menu = a
                if "view_of" not in st.session_state:
                    st.session_state.view_of = b
                st.rerun()
        reset_workspace()
    
# -------------------------------
# View state tracker (used across pages)
# -------------------------------

if "view_of" not in st.session_state:
    st.session_state.view_of = {}

# -------------------------------
# Page Routing Logic
# -------------------------------
if selected_sidebar == "Import Model":
    import_model.show(engineering_nodes=engineering_nodes, engineering_edges=engineering_edges,
                       sustainability_nodes=sustainability_nodes, sustainability_edges=sustainability_edges)

elif selected_sidebar == "Build PPR Model":
    build_ppr.show(engineering_nodes=built_engineering_nodes, engineering_edges=built_engineering_edges,
                   sustainability_nodes=built_sustainability_nodes, sustainability_edges=built_sustainability_edges)

elif selected_sidebar == "Explore Sample":
    explore_sample.show(engineering_nodes=sample_eng_nodes, engineering_edges=sample_eng_edges,
                   sustainability_nodes=sample_sus_nodes, sustainability_edges=sample_sus_edges)

elif selected_sidebar == "Help and Docs":
    help_docs.show()
