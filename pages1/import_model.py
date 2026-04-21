import streamlit as st
from xml.etree import ElementTree as et


#Local application imports
from pages1.views import ppr_view
from pages1.views import additonal_views
from pages1.Utils1 import viewpoints_menu
from pages1.Utils1.aml_utils import build_elements_dict, extract_links, extract_ppr_links, iface_mapping
from pages1.data.config_data import global_nodes_list
from pages1.Utils1.excel_utils import parse_excel
from pages1.Utils1 import ppr_conform


def show(engineering_nodes: dict, engineering_edges: list, sustainability_nodes: dict, sustainability_edges: list):
    """
    Handles model import workflow:
    - Upload AML / Excel file
    - Parse into nodes and edges
    - Validate PPR conformity
    - Render selected viewpoint (PPR, Engineering, Sustainability)
    """
    st.header("📥 Import Model")
    

    # -------------------------------
    # Session state initialization
    # -------------------------------

    if "upload" not in st.session_state:
        st.session_state.upload = None  # Stores uploaded file name
    
    if "error_details" not in st.session_state:
        st.session_state.error_details= None  # Stores PPR conformity errors

    # -------------------------------
    # File Upload Section (only if no file loaded)
    # -------------------------------
    
    if st.session_state.upload is None:       
        st.subheader("Upload an AML/XLXS file to visualize and analyze the PPR model.")

        # Prevent upload if a model is already built in workspace
        if st.session_state.built_nodes:
            lock1= True
            st.warning("""⚠️ **Workspace Already in Use**. A PPR model is currently active in the workspace. To upload a new file, please reset the workspace first.""")
        else:
            lock1=False
        uploaded_file= st.file_uploader("Upload AML/XLXS file", type=["aml", "xlsx"], key="file_uploader", disabled=lock1)
 

        # -------------------------------
        # File Processing
        # -------------------------------
        if uploaded_file:
            file_name = uploaded_file.name.lower()
            #Check separately for AML and XLSX files
            if file_name.endswith(".aml"):
                try:
                    tree= et.parse(uploaded_file)
                    root= tree.getroot()
                    ns = {"caex": "http://www.dke.de/CAEX"}

                except Exception as e:
                    st.warning("Your AML file might be corrupted.")
                    with st.expander ("Full error"):
                        st.write(e)

                # Extract elements and relationships
                elements_dict=build_elements_dict(root, ns)
                link_list= extract_links(root, ns)
                iface_mappi= iface_mapping(root, ns)

                # Convert raw links to PPR-specific relationships
                ppr_link_list = extract_ppr_links(link_list, iface_mapping_dict=iface_mappi, elements= elements_dict)
                st.session_state.upload = uploaded_file.name  # Mark file as processed and save file name

                #Storing extracted data in session_state
                if "imported_nodes" not in st.session_state:
                    st.session_state.imported_nodes = elements_dict.copy() 

                if "imported_edges" not in st.session_state:
                    st.session_state.imported_edges = ppr_link_list.copy() 

            
            # -------- Excel Processing --------
            elif file_name.endswith(".xlsx"):
                # elements_dict = elements_from_excel(uploaded_file)
                # ppr_link_list = links_from_excel(uploaded_file)

                try:
                    elements_dict, ppr_link_list = parse_excel(uploaded_file)

                except ValueError as e:
                    st.error(str(e))
                    return



            st.session_state.upload = uploaded_file.name  # Mark file as processed
            if "imported_nodes" not in st.session_state:
                st.session_state.imported_nodes = elements_dict.copy()  # Store a copy of the elements dictionary in session state

            if "imported_edges" not in st.session_state:
                st.session_state.imported_edges = ppr_link_list.copy()  # Store a copy of the link list in session state


            # -------------------------------
            # PPR Conformance Validation
            # Step 1: Node validation
            # Step 2: Edge validation (only if nodes are valid)
            # if invalid, then store PPR unconformity errors in session_state
            # -------------------------------
            errors=[]
            errors = ppr_conform.validate_nodes (imported_nodes=elements_dict, imported_edges=ppr_link_list)
            if errors:
                st.session_state.error_details= errors
            
            else:
                errors=ppr_conform.validate_edges(imported_nodes=elements_dict, imported_edges=ppr_link_list)
                if errors:
                    st.session_state.error_details= errors
            


    # -------------------------------
    # Post-upload: Visualization Section
    # -------------------------------
    if st.session_state.upload is not None:
        imported_nodes= st.session_state.imported_nodes
        imported_edges= st.session_state.imported_edges   
        st.markdown(f"Uploaded File is {st.session_state.upload}.")
            
        # Display validation errors (if any) and prevent further workspace use
        if st.session_state.error_details is not None:
            st.error(f"⚠️The uploaded file does not comply with the PPR format. Refer to **Help and Docs** to learn what makes a model PPR-conform.")
            for err in st.session_state.error_details:
                st.error(err)


        else:
            # -------------------------------
            # Viewpoint selection (PPR / Engineering / Sustainability)
            # -------------------------------
            selected_view = viewpoints_menu.handle("Import Model")
            if selected_view=="PPR View":
                ppr_view.show(nodes=imported_nodes, links=imported_edges,
                                engineering_nodes=engineering_nodes, engineering_edges=engineering_edges,
                                sustainability_nodes=sustainability_nodes, sustainability_edges=sustainability_edges)
            if selected_view=="Engineering View":
                additonal_views.show(ppr_nodes=imported_nodes, nodes=engineering_nodes, links=engineering_edges, selected_view=selected_view)
            if selected_view=="Sustainability View":
                additonal_views.show(ppr_nodes=imported_nodes, nodes=sustainability_nodes, links=sustainability_edges, selected_view=selected_view)



