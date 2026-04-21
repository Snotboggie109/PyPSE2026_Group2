import pandas as pd
from pages1.data import config_data

REQUIRED_SHEETS = ["Nodes", "Edges"]
REQUIRED_NODE_COLUMNS = ["Node_ID", "Name"]
REQUIRED_EDGE_COLUMNS = ["Start Node", "End Node"]


# -----------------------------
# VALIDATION
# -----------------------------
def validate_excel(file_path):
    try:
        xls = pd.ExcelFile(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {e}")

    missing_sheets = [s for s in REQUIRED_SHEETS if s not in xls.sheet_names]
    if missing_sheets:
        raise ValueError(
            f"Missing required sheet(s): {missing_sheets}. "
            f"Available sheets: {xls.sheet_names}"
        )

    df_nodes = pd.read_excel(xls, sheet_name="Nodes")
    df_edges = pd.read_excel(xls, sheet_name="Edges")

    missing_node_cols = [c for c in REQUIRED_NODE_COLUMNS if c not in df_nodes.columns]
    if missing_node_cols:
        raise ValueError(
            f"Missing required column(s) in 'Nodes': {missing_node_cols}. "
            f"Available columns: {list(df_nodes.columns)}"
        )

    missing_edge_cols = [c for c in REQUIRED_EDGE_COLUMNS if c not in df_edges.columns]
    if missing_edge_cols:
        raise ValueError(
            f"Missing required column(s) in 'Edges': {missing_edge_cols}. "
            f"Available columns: {list(df_edges.columns)}"
        )

    return xls


# -----------------------------
# NODE MAP
# -----------------------------
def build_node_lookup(df_nodes):
    return {
        str(row["Node_ID"]).strip(): {
            "name": str(row["Name"]).strip(),
            "type": row["PPR_Type"]
        }
        for _, row in df_nodes.iterrows()
    }


def validate_cardinality(value, row_index):
    if pd.isna(value) or value == "":
        return None

    if isinstance(value, (int, float)) and float(value).is_integer():
        return int(value)

    if isinstance(value, str):
        if value.strip().isdigit():
            return int(value.strip())

    raise ValueError(
        f"Invalid Cardinality at row {row_index + 2}: '{value}'. "
        f"Must be an integer or empty."
    )


# -----------------------------
# NODES
# -----------------------------
def elements_from_excel(xls: pd.ExcelFile):
    df_nodes = pd.read_excel(xls, sheet_name="Nodes")

    elements = {}

    for _, row in df_nodes.iterrows():
        if pd.isna(row["Node_ID"]) or pd.isna(row["Name"]):
            continue

        node_id = str(row["Node_ID"]).strip()
        name = str(row["Name"]).strip()
        ppr_type = row.get("PPR_Type")

        attributes = []
        for col in df_nodes.columns:
            if col not in ["Node_ID", "Name", "PPR_Type"]:
                value = row.get(col)
                if pd.notna(value):
                    attributes.append({
                        "attr_name": col,
                        "data_type": None,
                        "value": str(value)
                    })

        elements[name] = {
            "name": name,
            "id": node_id,
            "class": ppr_type,
            "xml": None,
            "port_id": None,
            "parent": None,
            "attributes": attributes
        }

    return elements


# -----------------------------
# LINKS
# -----------------------------
def links_from_excel(xls: pd.ExcelFile):
    df_nodes = pd.read_excel(xls, sheet_name="Nodes")
    df_edges = pd.read_excel(xls, sheet_name="Edges")

    node_lookup = build_node_lookup(df_nodes)

    links = []

    for idx, row in df_edges.iterrows():

        if pd.isna(row["Start Node"]) or pd.isna(row["End Node"]):
            continue

        source_id = str(row["Start Node"]).strip()
        target_id = str(row["End Node"]).strip()

        source_data = node_lookup.get(source_id)
        target_data = node_lookup.get(target_id)

        if source_data is None or target_data is None:
            continue

        source = source_data["name"]
        target = target_data["name"]

        source_type = source_data["type"]
        target_type = target_data["type"]

        parent_child = source_type == target_type

        cardinality = validate_cardinality(row.get("Cardinality"), idx)

        links.append({
            "name": f"{source}_to_{target}",
            "source": source,
            "target": target,
            "type": config_data.edgeType_by_view["PPR View"][0],
            "cardinality": cardinality,
            "parent_child": parent_child
        })

    return links


def apply_parent_relationships(elements, links):
    for link in links:
        if link.get("parent_child") is True:
            source = link["source"]
            target = link["target"]

            for node in elements.values():
                if node["name"] == target:
                    node["parent"] = source
                    break

    return elements


# -----------------------------
# MAIN ENTRY POINT
# -----------------------------
def parse_excel(file_path):
    xls = validate_excel(file_path)

    elements = elements_from_excel(xls)
    links = links_from_excel(xls)

    elements = apply_parent_relationships(elements, links)

    return elements, links