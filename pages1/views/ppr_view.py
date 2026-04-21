import streamlit as st


#Local application imports
from pages1.data.config_data import PPR_ATTRS, ENG_ATTRS, SUST_ATTRS, edgeType_by_view, global_nodes_list, ppr_edge_type_mapping
from pages1.Utils1.graph_utils import nx_Digraph, node_cardinality_mapping, show_yfiles_graph, nx_to_yfiles_graph
from pages1.Utils1.helper_functions import nodes_by_class, has_descendants, delete_node_recursive, get_cardinality_by_name
from pages1.Utils1 import req_check

def show(nodes: dict, links: list, engineering_nodes: dict, engineering_edges: list,
           sustainability_nodes: dict, sustainability_edges: list,locked: bool = False,): 
    """
    Core visualization and interaction module for PPR models.

    Responsibilities:
    - Display interactive graph (yFiles)
    - Enable CRUD operations on nodes and edges
    - Enforce PPR constraints during editing
    - Provide requirement validation checks

    This module is reused by:
    - Import Model (import_model.py)
    - Build PPR Model (build_ppr.py)
    - Explore Sample (explore_sample.py)
    """
    
    
    selected_view= "PPR View"
    grouped_nodes= nodes_by_class(nodes)
    all_nodes= [node for node in nodes.keys()]
    link_names_to_delete= [link["name"] for link in links if not link.get("parent_child",False)]
    product_nodes = grouped_nodes.get("Product", [])
    process_nodes = grouped_nodes.get("Process", [])

    product_to_process_links = [
        link["name"]
        for link in links
        if link["source"] in product_nodes and link["target"] in process_nodes
    ]

    c1, c2 = st.columns([1,3]) # Layout: (c1) Control Panel + (c2) Graph View
    with c1:
        active_panel = st.segmented_control(
            "PPR view panel",
            options=["🏗️ Edit Network", "🗑️ Delete Components", "✅ Requirement Check"],
            default="🏗️ Edit Network",
            key="ppr_active_panel",
            width="stretch"
        )

        if active_panel == "🏗️ Edit Network":
            grouping= False # Boolean for grouping in the yfiles Graph
            ppr_radio=st.radio("What do you want to do?",["Create PPR Node","Create PPR Edge","Update PPR Node", "Update Cardinality"], key="create_node_or_edge_or_check")
            with st.container(border=True,key="ppr_node_container"):
                if ppr_radio == "Create PPR Node":
                    st.markdown("#### Create PPR Node")
                    node_type= st.selectbox("Node Type", global_nodes_list,key="node_type_select")
                
                    with st.form(key="create_ppr_node_form"):
                        node_name= st.text_input("Node Name",disabled=locked)
                        parent_node = st.selectbox("Choose Parent", options= grouped_nodes.get(node_type, []),
                                                    disabled=locked, key="parent_node_select",index=None,
                                                    help="Choose the parent of this node if there is one. If none, select none.")                   
                        selected_ppr_attrs= []
                        if PPR_ATTRS[node_type]:  # Check if there are attributes defined for this element type
                            available_attrs= list(PPR_ATTRS[node_type].keys())
                            for attr in available_attrs:
                                attr_options = PPR_ATTRS[node_type][attr]["options"]
                                chosen_value= st.selectbox(f"Choose {attr} attribute", options=attr_options, index=None, key=f"{node_type}_{attr}")
                                selected_ppr_attrs.append({"attr_name": attr, "value": chosen_value})

                        elem_data={}
                        submitted= st.form_submit_button("Create Node", disabled=locked, key="create_node_button")

                        if submitted:
                        #Also check if there are duplicate node names here before creating the element. Check if empty node name is allowed or not.
                            if not node_name.strip():
                                st.error("🚨 **Validation Error:** Node Name cannot be empty.")
                            else: 
                                node_name=" ".join(node_name.strip().split())
                                node_name = node_name[0].upper() + node_name[1:]

                                if node_name in all_nodes:
                                    st.error("🚨 **Validation Error:** A node with this name already exists. Please choose a different name.")
                                else:
                                        elem_data = {
                                            "name": node_name,
                                            "class": node_type,
                                            "parent": parent_node,
                                            "attributes": selected_ppr_attrs
                                        }
                                        nodes[node_name] = elem_data  # Add the new node to the nodes dictionary
                                        if parent_node:
                                            links.append({"name":parent_node + "_to_" + node_name,
                                                        "source": parent_node,
                                                    "target": node_name,"type":"PPR_port", "cardinality": None, "parent_child":True})
                                        st.success(f"Node {node_name} of type **{node_type}** created!")
                                        st.rerun()

                if ppr_radio == "Create PPR Edge":                    
                    st.markdown("#### Create PPR Edge")
                    edge_type= st.selectbox("Edge Type",list(ppr_edge_type_mapping.keys()),index=None, key="edge_type_select")
                    source_class, target_class= ppr_edge_type_mapping.get(edge_type, (None, None))
                    with st.form(key="create_ppr_edge_form"):                                                   
                        source_node= st.selectbox(f"Source Node ({source_class})",options=grouped_nodes.get(source_class,[]), index=None)
                        target_node= st.selectbox(f"Target Node ({target_class})",options=grouped_nodes.get(target_class,[]), index=None)
                        if edge_type =="Product → Process":     #Cardinality is only avaialable for this ppr_edge_type                     
                            cardinality = st.number_input("Cardinality (optional)", min_value=2,step=1,value=None)
                        
                        submitted_edge= st.form_submit_button("Create Edge", disabled=locked, key="create_ppr_edge")
                        if submitted_edge:
                            if source_node is None or target_node is None:
                                st.error("🚨 **Validation Error:** You must select both a Source and a Target node to create a link.")
                            else:
                                duplicate_exists =any(link for link in links if link["source"] == source_node and link["target"] == target_node) 
                                reverse_link_exists= any(link for link in links if link["source"] == target_node and link["target"] == source_node)
                                if duplicate_exists:
                                    st.error(f"🚨 **Validation Error:** An edge between **{source_node}** and **{target_node}** already exists. Please choose a different combination.")
                                elif reverse_link_exists:
                                    st.error(f"🚨 **Validation Error:** An edge between **{target_node}** and **{source_node}** alreay exists. Circular or bi-directional edges are not permitted in this PPR model.")
                                elif edge_type == "Product → Process":
                                        process_nodes = grouped_nodes.get("Process", [])
                                        product_already_linked = any(link for link in links
                                            if link["source"] == source_node and link["target"] in process_nodes)

                                        if product_already_linked:
                                            st.error( f"🚨 **Constraint Violation:** Product **{source_node}** is already connected to a Process.")
                                        else:
                                            links.append({"name":source_node + "_to_" + target_node,"source": source_node,
                                                    "target": target_node, "type":"PPR_port","cardinality": cardinality, "parent_child":False})
                                            st.success(f"Edge of type **{edge_type}** created between **{source_node}** and **{target_node}**!")
                                else:
                                        
                                        links.append({"name":source_node + "_to_" + target_node,"source": source_node,
                                                    "target": target_node, "type":"PPR_port","cardinality": None, "parent_child":False})
                                        st.success(f"Edge of type **{edge_type}** created between **{source_node}** and **{target_node}**!")
                                        st.rerun()

                if ppr_radio == "Update PPR Node":
                    st.markdown("#### Update PPR Node")
                    node_type = st.selectbox("Node Type", global_nodes_list, key="ppr_node_type_select")
                    selected_node = st.selectbox("Choose Node to update", options=grouped_nodes.get(node_type, []), index=None,  key="ppr_node_name_select")
                    
                    with st.form(key="update_ppr_node_form"):
                        selected_ppr_attrs = []                           
                        existing_attrs={} #For storing the existing attribute values of the selected node to pre-populate the input fields
                        if selected_node:
                            for attr_item in nodes[selected_node].get("attributes",[]):
                                existing_attrs[attr_item["attr_name"]]= attr_item.get("value", None)
                        if PPR_ATTRS[node_type]:  # Check if there are attributes defined for this node type
                            available_attrs_update = list(PPR_ATTRS[node_type].keys())
                            for attr in available_attrs_update:
                                st.text("Adjust Attribute:")
                                attr_options= PPR_ATTRS[node_type][attr]["options"]
                                default_val= existing_attrs.get(attr,None)
                                if default_val in attr_options:
                                    default_index = attr_options.index(default_val)
                                else:
                                    default_index= None
                                value= st.selectbox(f"{attr.title()}", options=attr_options, index= default_index, disabled=locked, key=f"{selected_node}_{attr}_value")
                                selected_ppr_attrs.append({"attr_name": attr, "value": value})

                        submitted = st.form_submit_button("Update Node", disabled=locked, key="update_node_button")
                        if submitted:
                            if selected_node is None:
                                st.error(f"🚨 **Validation Error:** You must select a node to update.")
                            
                            elif not PPR_ATTRS[node_type]:
                                st.error(f"🚨 **Validation Error:** Node **{selected_node}** has no configurable attributes to update")
                            
                            else:
                                new_attrs={item["attr_name"]: item["value"] for item in selected_ppr_attrs}
                                if existing_attrs== new_attrs:
                                    st.error(f"🚨 No changes detected for node **{selected_node}**. Attributes are same as before.")
                                else:
                                    nodes[selected_node]["attributes"] = selected_ppr_attrs #Updating the attribute values
                                    st.success(f"Node **{selected_node}** updated")
                        
                if ppr_radio == "Update Cardinality":
                    st.markdown("#### Update Cardinality")
                    update_edge_type= st.selectbox("Edge Type",options=["Product → Process"], key="update_ppr_edge_type")
                    edge_to_update= st.selectbox("Select Edge to Update",options=product_to_process_links, index=None, key="edge_to_upd_select")
                    with st.form(key="update_ppr_edge_form"): 
                        default_val= get_cardinality_by_name(links=links, name=edge_to_update)
                        default_val = int(default_val) if default_val else None                      
                        cardinality = st.number_input("Cardinality (optional)", min_value=2,step=1,value=default_val, disabled=locked,key= f"{edge_to_update}_card")                          
                        submitted_update_edge= st.form_submit_button("Update Cardinality", disabled=locked, key="update_ppr_edge")

                        if submitted_update_edge:
                            if edge_to_update is None:
                                st.error("🚨 **Validation Error:** You must select an edge to update its cardinality.")
                            elif default_val == cardinality:
                                st.error(f"🚨 **Validation Error:** No changes detected. The cardinality for edge **{edge_to_update}** is unchanged.")
                            else:
                                for link in links:
                                    if link["name"] == edge_to_update:
                                        link["cardinality"] = cardinality
                                        break
                                st.success(f"✅ Cardinality for **{edge_to_update}** updated successfully.")
                                st.rerun()
                            

                            
                                                    
        elif active_panel == "🗑️ Delete Components":
            grouping= False # Boolean for grouping in the yfiles Graph
            ppr_del_radio=st.radio("What do you want to do?",["Delete Node", "Delete Edge"], key="del_node_or_edge")
            with st.container(border=True,key="ppr_del_container"):
                if ppr_del_radio == "Delete Node":
                    st.markdown("#### Delete PPR Node")
                    del_node_type= st.selectbox("Node Type",global_nodes_list,key="del_node_type_select")
                    with st.form(key="delete_ppr_node_form"):
                        node_to_delete= st.selectbox("Select Node to Delete", options=grouped_nodes.get(del_node_type,[]), index=None, key="node_to_del_select") # Replace with actual list of nodes from the graph
                        submitted_del_node= st.form_submit_button("Delete Node", disabled=locked)
                        if submitted_del_node:
                            if node_to_delete is None:
                                st.error("🚨 **Validation Error:** You must select a node to delete.")
                            else:
                                if has_descendants (node_to_delete=node_to_delete, nodes_dict=nodes):
                                    delete_node_recursive(node_to_delete=node_to_delete, nodes_dict= nodes, links=links,
                                                            engineering_edges=engineering_edges, engineering_nodes=engineering_nodes,
                                                            sustainability_edges=sustainability_edges, sustainability_nodes=sustainability_nodes
                                                            )
                                    st.success(f"Node **{node_to_delete}**  and its children deleted!")
                                else:
                                    delete_node_recursive(node_to_delete=node_to_delete, nodes_dict= nodes, links=links,
                                                                engineering_edges=engineering_edges, engineering_nodes=engineering_nodes,
                                                                sustainability_edges=sustainability_edges, sustainability_nodes=sustainability_nodes
                                                                )
                                    st.success(f"Node **{node_to_delete}** deleted!")
                                    st.rerun()

                if ppr_del_radio == "Delete Edge":
                    st.markdown("#### Delete PPR Edge")
                    del_edge_type= st.selectbox("Edge Type", edgeType_by_view[selected_view], key="del_edge_type_select")
                    with st.form(key="delete_ppr_edge_form"):
                        edge_to_delete= st.selectbox("Select Edge to Delete", options=link_names_to_delete,index=None, key="edge_to_del_select") # Replace with actual list of edges from the graph
                        submitted_del_edge= st.form_submit_button("Delete Edge", disabled=locked)
                        if submitted_del_edge:
                            if edge_to_delete is None:
                                st.error("🚨 **Validation Error:** You must select an edge to delete.")
                            else:
                                for i in range(len(links)-1, -1, -1):  # Iterate backwards to avoid index issues when deleting
                                    if links[i]["name"] == edge_to_delete and links[i]["type"] == del_edge_type:
                                        del links[i]  # Remove the link from the links list
                                        st.success(f"Edge **{edge_to_delete}** deleted!")
                                        st.rerun()
                                        break

        elif active_panel == "✅ Requirement Check":
            grouping= True # Boolean for grouping in the yfiles Graph
            nx_ppr_graph=  nx_Digraph(nodes_dict=nodes, link_list=links)
            req_check.ppr_req_checks(nx_graph=nx_ppr_graph)




    with c2:
        nx_ppr_graph=  nx_Digraph(nodes_dict=nodes, link_list=links)     
        node_cardinality= node_cardinality_mapping(nx_ppr_graph)
        nodes, edges = nx_to_yfiles_graph(nx_ppr_graph,node_cardinality)
        show_yfiles_graph(nodes, edges, grouping=grouping)

