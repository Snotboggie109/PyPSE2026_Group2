
"""
Config Data Module

This module defines the core configuration and semantic mappings used
throughout the PPR (Product–Process–Resource) visualization application.

It centralizes all domain-specific constants (Meta-Model), including:
- Valid node types
- Allowed edge relationships across viewpoints
- View-specific edge types
- Attribute definitions for different views

Configuration details:

- global_nodes_list:
  Defines the valid PPR node classes (Product, Process, Resource).
  Used for node validation and classification.

- ppr_edge_type_mapping:
  Defines allowed relationships between node types in the PPR model
  (e.g., Product → Process, Process → Resource).

- edgeType_by_view:
  Maps different visualization views to their corresponding edge types:
    • PPR View → structural PPR connections
    • Engineering View → functional/engineering relationships
    • Sustainability View → environmental interactions

- PPR_ATTRS, ENG_ATTRS, SUST_ATTRS:
  Define attribute schemas for each node type under different views.
  Each attribute includes:
    • data type (int, float, list)
    • optional units
    • predefined options (for categorical values)

- VIEW_ATTRS_MAPPING:
  Links each view to its corresponding attribute definitions,
  enabling dynamic attribute handling based on selected view.

Purpose:
- Ensures consistency across the application
- Supports validation, UI rendering, and data modeling
- Acts as a META-model for PPR semantics and attributes
"""
global_nodes_list = ["Product", "Process", "Resource"]

ppr_edge_type_mapping = {
    "Product → Process": ("Product", "Process"),
    "Process → Product": ("Process", "Product"),
    "Process → Resource": ("Process", "Resource"),
}

edgeType_by_view= {
    "PPR View": ["PPR_port"],
    "Engineering View": ["part_of", "contributes_to", "impacts", "constraints"],
    "Sustainability View": ["energy_flows", "material_flows", "influences"]
}

# PPR View Attributes
PPR_ATTRS = {
    "Product": {
        "color": {"type": list, "options": ["Red", "Blue", "Green", "Black", "Yellow", "White"]},
        "size": {"type": list, "options": ["Small", "Medium", "Big"]}
    },
    "Process": {},
    "Resource": {}
}

# Engineering View Attributes
ENG_ATTRS = {
    "Product": {
        "product_cost": {"type": float, "unit": "Euro"}
    },
    "Process": {
        "cycle_time": {"type": float, "unit": "seconds"}
    },
    "Resource": {
        "operating_speed": {"type": float, "unit": "Units/min"},
        "operating_cost": {"type": float, "unit": "Euro"}
    }
}

# Sustainability View Attributes
SUST_ATTRS = {
    "Product": {
        "durability": {"type": int, "unit": "years"},
        "co2_per_unit": {"type": float, "unit": "kg/unit"}
    },
    "Process": {
        "specific_energy_consumption": {"type": float, "unit": "KW/unit"},
        "co2_emission": {"type": float, "unit": "kg/hr"}
    },
    "Resource": {
        "energy_flow_rate": {"type": float, "unit": "KW/hr"}
    }
}

VIEW_ATTRS_MAPPING = {
    "PPR View": PPR_ATTRS,
    "Engineering View": ENG_ATTRS,
    "Sustainability View": SUST_ATTRS
}

