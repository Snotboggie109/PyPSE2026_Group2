import streamlit as st

#Local application imports
from pages1.Utils1.graph_utils import nx_Digraph, node_cardinality_mapping, show_yfiles_graph, nx_to_yfiles_graph
from pages1.data.config_data import PPR_ATTRS, ENG_ATTRS, SUST_ATTRS, edgeType_by_view, global_nodes_list, VIEW_ATTRS_MAPPING
from pages1.Utils1.helper_functions import nodes_by_class,edges_by_type,extract_numeric, are_attributes_same, remove_links_of_node
from pages1.Utils1 import req_check


def show(ppr_nodes: dict, nodes: dict,links: list, selected_view: str, locked: bool = False):    

    """
    Handles Engineering and Sustainability views.
    Responsibilities:
    - Extend PPR nodes with domain-specific attributes
    - Allow view-specific edge creation
    - Support deletion and requirement checking
    - Render graph visualization

    Key idea:
    These views are *projections* of the base PPR model,
    enriched with additional attributes and relationships.

    This module is reused by:
    - Import Model (import_model.py)
    - Build PPR Model (build_ppr.py)
    - Explore Sample (explore_sample.py)
    """  
    
    view_name= selected_view.split()[0] # Extracting 'PPR', 'Engineering', or 'Sustainability' from the selected view
    grouped_nodes= nodes_by_class(ppr_nodes)
    all_nodes= [node for node in ppr_nodes.keys()]
    view_grouped_nodes= nodes_by_class(nodes)
    view_all_nodes= [node for node in nodes.keys()]
    view_grouped_edges= edges_by_type(links)
    view_link_names= [link["name"] for link in links]


    VIEW_ATTRS = VIEW_ATTRS_MAPPING.get(selected_view)
    VIEW_EDGE_TYPES=edgeType_by_view[selected_view]
    col1,col2= st.columns([1,3])

    with col1:
        active_panel = st.segmented_control(
            f"{view_name} view panel",
            options=["🏗️ Edit Network", "🗑️ Delete Components", "✅ Requirement Check"],
            default="🏗️ Edit Network",
            key=f"{view_name}_active_panel",
            width="stretch"
        )
        # with tab_create:
        if active_panel == "🏗️ Edit Network":
            view_radio=st.radio("What do you want to do?",[f"Add or Modify Node",
                                                            f"Create Edge"],
                                                            key=f"adjust_{view_name}_node_or_edge")
            with st.container(border=True,key="view_adjust_container"):
                if view_radio == f"Add or Modify Node":
                    st.markdown(f"#### Add Node to {view_name} view")
                    node_type= st.selectbox("Node Type",global_nodes_list,key=f"{view_name}_node_type_select")
                    selected_node = st.selectbox("Choose Node", options=grouped_nodes.get(node_type, []),
                                                    key=f"{view_name}_node_select", index=None)

                    with st.form(key=f"add_node_to_{view_name}_form"):                   
                        selected_ppr_attrs= []
                        existing_attrs={} #For storing the existing attribute values of the selected node to pre-populate the input fields
                        if selected_node:
                            if selected_node in nodes:
                                for attr_item in nodes[selected_node].get("attributes", []):
                                    existing_attrs[attr_item["attr_name"]] = extract_numeric(attr_item.get("value", "0"))
                        if VIEW_ATTRS[node_type]:  # Check if there are attributes defined for this node type                         
                            available_attrs= list(VIEW_ATTRS[node_type].keys())
                            for attr in available_attrs:
                                attrs_info= VIEW_ATTRS[node_type][attr]
                                unit= attrs_info["unit"]
                                st.text("Adjust Attribute:")
                                default_val= existing_attrs.get(attr, 0.0)
                                col1_1, col1_2 = st.columns([2, 1])   
                                with col1_1:
                                    value = st.number_input(f"{attr.replace('_', ' ').title()}",
                                                            value=default_val,
                                                            disabled=locked,
                                                            min_value=0.0,step=1.0,format="%.2f",key=f"{selected_node}_{attr}_value")
                                with col1_2:
                                    st.text_input("Unit",value=unit,disabled=True,key=f"{attr}_unit")
                                selected_ppr_attrs.append({"attr_name": attr, "value": f"{value} {unit}"})

                        elem_data={}
                        submitted= st.form_submit_button("Add/Update Node",disabled=locked, key="add_node_button_view")

                        if submitted:
                                if selected_node is None:
                                    st.error("🚨 **Validation Error:** You must select a node to add to the view.")
                                elif selected_node not in nodes:
                                    elem_data = {
                                        "name": selected_node,"class": node_type,
                                        "parent": ppr_nodes[selected_node].get("parent", None),
                                        "attributes": selected_ppr_attrs}
                                    nodes[selected_node] = elem_data  # Add the new node to the nodes dictionary
                                    st.success(f"Node **{selected_node}** added to {view_name} view!")
                                    st.rerun()
                                elif selected_node in nodes:
                                    old_attrs_numeric= existing_attrs
                                    if are_attributes_same(old_attrs_numeric, selected_ppr_attrs):
                                        st.error(f"No changes detected for node **{selected_node}**. Attributes are the same as before.")
                                    else:
                                        elem_data = {"name": selected_node,"class": node_type,
                                                        "parent": ppr_nodes[selected_node].get("parent", None),
                                                        "attributes": selected_ppr_attrs}
                                        nodes[selected_node] = elem_data  # Add the new node to the nodes dictionary
                                        st.success(f"Node **{selected_node}** updated to {view_name} view!")
                                        st.rerun()
                        # st.write(nodes)
                
                if view_radio == f"Create Edge":
                    st.markdown(f"#### Create {view_name} view Edge")
                    with st.form(key=f"create_{view_name}_edge_form"):
                        view_edge_type= st.selectbox("Edge Type", VIEW_EDGE_TYPES, key=f"{view_name}_edge_type_select")
                        source_node= st.selectbox("Source Node Name",options=view_all_nodes, index=None)
                        target_node= st.selectbox("Target Node Name",options=view_all_nodes, index=None)
                        submitted_edge= st.form_submit_button("Create Edge", disabled=locked)
                        if submitted_edge:
                            if source_node is None or target_node is None:
                                st.error("🚨 **Validation Error:** You must select both a Source and a Target node to create a link.")
                            elif source_node == target_node:
                                st.error("🚨 **Validation Error:** Source and Target nodes cannot be the same.")
                            else:
                                duplicate_exists =any(link for link in links if link["source"] == source_node and link["target"] == target_node) 
                                if duplicate_exists:
                                    st.error("🚨 **Validation Error:** An edge between the selected Source and Target nodes already exists. Please choose a different combination.")  
                                else:                            
                                    links.append({"name": source_node + "_to_" + target_node,
                                                "source": source_node,
                                                "target": target_node,
                                                "type": view_edge_type
                                                })                     
                                    st.success(f"Edge of type **{view_edge_type}** created between {source_node} and {target_node}!")
                                    st.rerun()
                        # st.write(links)
                    
        elif active_panel == "🗑️ Delete Components":
            view_del_radio=st.radio("What do you want to do?",[f"Delete Node from {view_name} view", f"Delete Edge from {view_name} view"], key=f"{view_name}_del_node_or_edge")
            with st.container(border=True,key="view_delete_container"):
                if view_del_radio == f"Delete Node from {view_name} view":
                    st.markdown(f"#### Delete Node from {view_name} view")
                    view_del_node_type= st.selectbox("Node Type", global_nodes_list, key=f"del_{view_name}_node_type_select")
                    with st.form(key=f"delete_{view_name}_node_form"):
                        view_node_to_del= st.selectbox("Select Node to Delete", options=view_grouped_nodes.get(view_del_node_type, []),
                                                        index=None,
                                                        key=f"del_{view_name}_node_to_del_select")
                        submitted_del_view_node= st.form_submit_button(f"Delete Node", disabled=locked)
                        if submitted_del_view_node:
                            if view_node_to_del is None:
                                st.error("🚨 **Validation Error:** You must select a node to delete.")
                            else:
                                remove_links_of_node(links, view_node_to_del)  # Remove all links associated with the node
                                nodes.pop(view_node_to_del, None)  # Remove the node from the nodes dictionary  # Iterate backwards to avoid index issues when deleting
                                st.success(f"Node **{view_node_to_del}** of type **{view_del_node_type}** deleted from {view_name} view!")
                                st.rerun()


                if view_del_radio == f"Delete Edge from {view_name} view":
                    st.markdown(f"#### Delete Edge from {view_name} view")
                    view_del_edge_type= st.selectbox("Edge Type", VIEW_EDGE_TYPES, key=f"del_{view_name}_edge_type_select")
                    with st.form(key=f"delete_{view_name}_edge_form"):
                        view_edge_to_del= st.selectbox("Select Edge to Delete", options=view_grouped_edges.get(view_del_edge_type, []),
                                                        index=None,
                                                        key=f"del_{view_name}_edge_to_del_select")
                        submitted_del_view_edge= st.form_submit_button("Delete Edge", disabled=locked)
                        if submitted_del_view_edge:
                            if view_edge_to_del is None:
                                st.error("🚨 **Validation Error:** You must select an edge to delete.")
                            else:
                                for i in range(len(links)-1, -1, -1):  # Iterate backwards to avoid index issues when deleting
                                    if links[i]["name"] == view_edge_to_del and links[i]["type"] == view_del_edge_type:
                                        del links[i]  # Remove the link from the links list
                                        st.success(f"Edge **{view_edge_to_del}** of type **{view_del_edge_type}** deleted from {view_name} view!")
                                        st.rerun()
                                        break
        # with req_check:
        elif active_panel == "✅ Requirement Check":
            selected_req = st.radio("What do you want to do?",[f"Check {view_name} Requirement"])
            with st.container(border=True,key=f"{view_name}_check_container"):
                if selected_req== f"Check {view_name} Requirement":
                    node_type_req = st.selectbox("Node Type", global_nodes_list, key=f"{view_name}_node_type_select_req_check")
                    selected_attr_req = st.selectbox(f"Select attribute to be checked for class: **{node_type_req}**",
                                                options=VIEW_ATTRS[node_type_req], key=f"{view_name}_attr_select_req_check")
                    req_check_ops = ["equal to (=)", "less than (<)", "greater than (>)", "less than or equal to (<=)",
                                    "greater than or equal to (>=)"]
                    fun_req = st.selectbox("Value should be...", options=req_check_ops)
                    val_req = st.number_input("Enter the value", min_value=0.0, step=0.1, format="%f",key=f"{view_name}_req_check_value")

                    if st.button("Check Run", key="attr_check"):
                        result_df = req_check.get_matching_elements_by_attribute(
                            nodes=nodes,
                            node_type=node_type_req,
                            selected_attr=selected_attr_req,
                            fun=fun_req,
                            val=val_req
                        )
                        if not result_df.empty:
                            st.success(f"Found {len(result_df)} matching node(s).")
                            st.dataframe(result_df, use_container_width=True)
                        else:
                            st.warning("No matching nodes found.")




    with col2:
        nx_view_graph = nx_Digraph(nodes_dict=nodes, link_list=links)
        nodes, edges = nx_to_yfiles_graph(nx_view_graph)
        show_yfiles_graph(nodes, edges)