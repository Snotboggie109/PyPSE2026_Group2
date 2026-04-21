import streamlit as st
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge, Layout, NodeStyle, NodeShape
import networkx as nx

"""
Graph Utilities Module

This module contains all graph-related functionality used in the application,
including graph construction, transformation, and visualization.

Available functions:
1. Build directed graph from PPR data        → nx_Digraph
2. Compute graph (edges) properties (e.g. cardinality) → node_cardinality_mapping
3. Map node classes to visual styles         → class_to_shape
4. Convert graph to yFiles format            → nx_to_yfiles_graph
5. Render interactive graph in Streamlit     → show_yfiles_graph
"""

#NX GRAPH RELATED UTILS
def nx_Digraph(nodes_dict: dict, link_list: list)-> nx.DiGraph:
    G=nx.DiGraph()
    for node in nodes_dict.values():
        G.add_node(
            node["name"], 
            name=node["name"],
            node_class=node["class"],  # Renamed 'class' to 'node_class' to avoid Python errors
            xml=node.get("xml", None),  # Optional: Store the original XML element if needed
            port_id=node.get("port_id", None),
            parent=node.get("parent", None),
            attributes=node.get("attributes", [])
        )

    for il in link_list:
        actual_source= il["source"]
        actual_target=il["target"]

        G.add_edge(actual_source, actual_target,label=il["type"],cardinal=il.get("cardinality", None))
    return G

def node_cardinality_mapping(G: nx.DiGraph) -> dict:
    mapping = {}
    for u, v, data in G.edges(data=True):
        card = data.get("cardinal", "")
        if not card:
            continue

        try:
            mapping[u] = int(card)
        except (ValueError, TypeError):
            pass
    return mapping

def class_to_shape(node):
    props = node.get("properties", {})
    node_class = props.get("class", "")

    if node_class == "Process":
        return NodeStyle(shape=NodeShape.RECTANGLE)

    elif node_class == "Product":
        return NodeStyle(shape=NodeShape.ELLIPSE,color="red")

    elif node_class == "Resource":
        return NodeStyle(shape=NodeShape.ROUND_RECTANGLE,color="green")

    else:
        return NodeStyle(shape=NodeShape.HEXAGON)

def show_yfiles_graph(nodes1, edges1, grouping=False):
    graph_args = dict(
        nodes=nodes1,
        edges=edges1,
        directed_mapping="True",
        edge_label_mapping=lambda edge: (
            edge["properties"]["label"]
            if edge["properties"]["label"] != "PPR_port"
            else ""
        ),
        node_styles_mapping=class_to_shape
    )
    # ✅ Add grouping ONLY if True
    if grouping:
        graph_args["node_parent_group_mapping"] = "class"
        layout = Layout.ORTHOGONAL
    else:
        layout = Layout.HIERARCHIC

    graph = StreamlitGraphWidget(**graph_args)
    graph.node_size_mapping = lambda node: ((90, 40) if node.get("properties", {}).get("parent") is not None else (120, 60))
    graph.show(graph_layout=layout, overview=False)

def nx_to_yfiles_graph(nx_graph,node_cardinality_mapping=None):
    nodes = []
    edges = []

    # ---- Nodes ----
    for node_id, attrs in nx_graph.nodes(data=True):
        parent = attrs.get("parent", None)
        attributes = attrs.get("attributes", [])
        base_label= attrs.get("name",str(node_id))

        #Append cardinality to label if exists
        card= node_cardinality_mapping.get(node_id) if node_cardinality_mapping else None
        label=f"{base_label}\n({card}x)" if card else base_label
        # Start with parent
        properties = {
            "parent": parent,
            "class": attrs.get("node_class",""),
            "label": label
        }

        # Flatten attributes list into properties
        for attr in attributes:
            attr_name = attr.get("attr_name")
            value = attr.get("value")

            if attr_name:
                properties[attr_name] = value

        nodes.append({
            "id": str(node_id),
            "properties": properties
        })
    # ---- Edges ----
    for source, target, attrs in nx_graph.edges(data=True):
        cardinality = attrs.get("cardinal", None)

        edges.append({
            "id": f"{source}-{target}",
            "start": str(source),
            "end": str(target),
            "cardinality": cardinality,
            "properties": {"label": attrs.get("label", "")}
        })

    return nodes, edges

