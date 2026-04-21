import streamlit as st
import pandas as pd
import networkx as nx

#Local application imports
from pages1.Utils1.helper_functions import extract_numeric

def ppr_req_checks(nx_graph):
    """
    Provides interactive requirement checks for the PPR graph using Streamlit UI.

    Includes:
    - Axle–Wheel connectivity check:
      Ensures that each Axle is connected to exactly two Wheels
      based on edge cardinalities (Wheel = 2 × Axle).

    - Disconnected nodes check:
      Identifies isolated nodes with no incoming or outgoing edges.
    """

    selected_req = st.radio(
        "What do you want to do?",
        [
            "Check Axle-Wheel Connectivity",
            "Check Disconnected Nodes"
        ]
    )

    with st.container(border=True,key="req_check_container"):
        if selected_req== "Check Axle-Wheel Connectivity":

            st.markdown("""
                **Description:**  
                In the PPR, every **Axle** must be connected to **exactly two Wheels** via a **Process**.  
                This rule verifies the relationship between Axle and Wheel components using connection cardinalities.

                **Rule:**  
                The total number of outgoing connections (cardinality) from **Wheel** must be **exactly twice** that of **Axle**.  
                Wheel Cardinality = 2 × Axle Cardinality  

                **Purpose:**  
                Ensures mechanical correctness and assembly feasibility.""")

            check_axle_wheel = st.button("Run Check", key="axle_wheel_check")
            if check_axle_wheel:
                axle_node = None
                wheel_node = None

                # ---- Find nodes by NAME ----
                for node, attrs in nx_graph.nodes(data=True):
                    node_name = attrs.get("name")

                    if node_name == "Axle":
                        axle_node = node
                    elif node_name == "Wheel":
                        wheel_node = node

                # ---- Validate existence ----
                if axle_node is None:
                    st.error("❌ No **Axle** node found")
                    return

                if wheel_node is None:
                    st.error("❌ No **Wheel** node found")
                    return

                # ---- Sum outgoing cardinalities ----
                axle_sum = sum(
                    int(attrs["cardinal"])
                    for _, _, attrs in nx_graph.out_edges(axle_node, data=True)
                    if attrs.get("cardinal") is not None
                )
                axle_sum= axle_sum if axle_sum > 0 else 1

                wheel_sum = sum(
                    int(attrs["cardinal"])
                    for _, _, attrs in nx_graph.out_edges(wheel_node, data=True)
                    if attrs.get("cardinal") is not None
                )

                if wheel_sum != 2 * axle_sum:
                    st.error(
                        f"❌ Cardinality mismatch: Wheel={wheel_sum}, Axle={axle_sum} "
                        f"(Expected: Wheel = 2 × Axle)"
                    )
                    return

                st.success(
                    f"✅ Requirement satisfied: An axle must be connected to two wheels "
                )




        if selected_req=="Check Disconnected Nodes":

            st.markdown("""
            **Description:**  
            The PPR **should not** contain isolated nodes.

            **Rule:**  
            All production nodes must be connected within the system.

            **Purpose:**  
            Prevents incomplete or invalid production flows.
            """)
        

            check_isolated = st.button("Run Check", key="check_isolated")

            if check_isolated:

                # Isolated nodes check
                isolated_nodes = [
                    node for node in nx_graph.nodes()
                    if nx_graph.in_degree(node) == 0 and nx_graph.out_degree(node) == 0
                ]

                if isolated_nodes:
                    st.warning("⚠️ Isolated nodes detected:")
                    isolated_info = []
                    for node in isolated_nodes:
                        node_class = nx_graph.nodes[node].get("node_class", "Unknown")
                        isolated_info.append({
                            "Node Name": node,
                            "Class": node_class
                        })
                    st.dataframe(isolated_info, use_container_width=True)
                else:
                    st.success("✅ No isolated nodes found.")
            
def get_matching_elements_by_attribute(nodes: dict, node_type: str, selected_attr: str, fun: str, val: float):
    """
    For additional viewpoints(engineering/sustainability), this filters nodes based on attribute conditions.

    Functionality:
    - Selects nodes of a specific class (Product, Process, Resource, etc.)
    - Extracts a given attribute from node attributes
    - Converts attribute values to numeric form
    - Applies a comparison condition (=, <, >, <=, >=)

    Returns:
        A pandas DataFrame containing matching nodes and their attribute values.

    Purpose:
    Supports querying and analysis of PPR elements on additional viewpoints based on attribute constraints.
    """    
    matching_rows = []

    for node_name, node_data in nodes.items():
        # Check only nodes of selected class
        if node_data.get("class") != node_type:
            continue

        # Find the selected attribute in node attributes
        attr_value_raw = None
        for attr_item in node_data.get("attributes", []):
            if attr_item.get("attr_name") == selected_attr:
                attr_value_raw = attr_item.get("value")
                break

        # Skip if attribute not present
        if attr_value_raw is None:
            continue

        # Convert value like "10 Euro" -> 10.0
        attr_value_num = extract_numeric(str(attr_value_raw))

        # Apply selected comparison
        condition_met = False

        if fun == "equal to (=)":
            condition_met = (attr_value_num == val)
        elif fun == "less than (<)":
            condition_met = (attr_value_num < val)
        elif fun == "greater than (>)":
            condition_met = (attr_value_num > val)
        elif fun == "less than or equal to (<=)":
            condition_met = (attr_value_num <= val)
        elif fun == "greater than or equal to (>=)":
            condition_met = (attr_value_num >= val)

        if condition_met:
            matching_rows.append({
                "Name": node_name,
                "Class": node_data.get("class"),
                "Attribute": selected_attr,
                "Value": attr_value_raw,
            })

    return pd.DataFrame(matching_rows)

