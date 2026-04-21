from collections import defaultdict
import streamlit as st
from pages1.data.config_data import global_nodes_list

"""
PPR Conform Module

This module validates whether an imported data conforms to
PPR (Product–Process–Resource) semantics.

It is used after importing AML/XLXS data and before visualization
to ensure that the graph structure follows correct PPR rules.

Validation functions included:

1. validate_one_product_one_process:  Checks that each Product is connected to only one Process
2. validate_product_to_resource: Checks for direct Product → Resource connections 
3. validate_cardinality: Ensures that cardinality is only defined for Product–Process connections and that the value is numeric.
4. validate_nodes: ensures nodes have valid classes (Product, Process, Resource)and no missing or invalid classifications.
5. validate_edges: Runs all edge-related validations, including: (1,2,3)

All functions return a list of errors describing violations,
which can be displayed in the Streamlit UI.
"""

def validate_one_product_one_process(nodes:dict, edges:list):
    product_process_map = defaultdict(set)
    errors = []

    for edge in edges:
        source = edge["source"]
        target = edge["target"]

        if source in nodes and target in nodes:
            source_class = nodes[source].get("class")
            target_class = nodes[target].get("class")

            # Product → Process link
            if source_class == "Product" and target_class != "Product":
                product_process_map[source].add(target)

    for product, processes in product_process_map.items():
        if len(processes) > 1:
            errors.append(
                f"❌ Product '{product}' is linked to multiple processes: {list(processes)}"
            )

    return errors

def validate_product_to_resource(nodes:dict, edges:list):
    errors = []

    for edge in edges:
        s, t = edge["source"], edge["target"]

        if s in nodes and t in nodes:
            if nodes[s]["class"] == "Product" and nodes[t]["class"] == "Resource":
                errors.append(
                    f"❌ Invalid edge Product → Resource: {s} → {t}"
                )

    return errors

def validate_cardinality(nodes:dict, edges:list):
    errors = []

    for edge in edges:
        s, t = edge["source"], edge["target"]
        cardinality = edge.get("cardinality")

        if s not in nodes or t not in nodes:
            continue

        s_class = nodes[s]["class"]
        t_class = nodes[t]["class"]

        is_product_process = (
            s_class == "Product" and t_class != "Product"
        )

        if is_product_process:
            # allow numeric cardinality only
            if cardinality is not None:
                try:
                    int(cardinality)
                except:
                    errors.append(
                        f"❌ Invalid cardinality '{cardinality}' on {s} → {t}"
                    )
        else:
            if cardinality is not None:
                errors.append(
                    f"❌ Cardinality must be NULL for non Product–Process link: {s} → {t}"
                )

    return errors

def validate_edges(imported_nodes:dict, imported_edges:list):
    errors = []
    errors += validate_one_product_one_process(nodes=imported_nodes, edges=imported_edges)
    errors += validate_product_to_resource(nodes=imported_nodes, edges=imported_edges)
    errors += validate_cardinality(nodes=imported_nodes, edges=imported_edges)
    return errors

def validate_nodes(imported_nodes:dict, imported_edges:list):
    errors=[]

    null_class_keys = [key for key, value in imported_nodes.items()
    if value.get("class") is None]

    invalid_class_keys = {
        key for key, value in imported_nodes.items()
        if value.get("class") not in global_nodes_list}

    if null_class_keys:
        errors.append(f"❌ No class keys found in imported nodes. Nodes missing class: {null_class_keys}. Fix and re-upload.")
        return errors

    elif invalid_class_keys:
        errors.append(f"**❌ Invalid class keys** found in imported nodes. Invalid classes: ***{invalid_class_keys}***. Please add the classes from following PPR conform semantics: **'Product'**, **'Process'** or **'Resource'**.")
        return errors


    elif not imported_nodes:
        errors.append("❌ No Nodes found in imported model.")
        return errors
 
    else: 
        return None

