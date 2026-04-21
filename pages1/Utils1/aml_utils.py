
#Local application imports
from pages1.data import config_data
"""
AML Utilities Module

This module handles the transformation of AML (CAEX) files into
an internal PPR graph representation.

Processing pipeline:
1. Extract elements and hierarchy        → build_elements_dict
2. Extract raw interface-based links     → extract_links
3. Map interfaces to elements            → iface_mapping
4. Convert to PPR element-level links    → extract_ppr_links

Key idea:
AML connections are defined via interfaces, which are resolved
to element-to-element relationships for PPR visualization.
"""

def build_elements_dict(root, ns):

    elements = {}   # ✅ local dictionary

    def extract_elements(elem, parent_name=None):
        elem_name = elem.get("Name")
        if elem_name:
            elem_name = " ".join(elem_name.strip().split()) 
            elem_name = elem_name[0].upper() + elem_name[1:]
        
        elem_id = elem.get("ID")
        elem_class= elem.get("RefBaseSystemUnitPath")
        elem_class = elem_class.split("/")[-1] if elem_class else None

        ppr_in_iface = elem.find("caex:ExternalInterface[@Name='PPR_in']", ns)
        ppr_out_iface= elem.find ("caex:ExternalInterface[@Name='PPR_out']", ns)
        port_in_id = ppr_in_iface.get("ID") if ppr_in_iface is not None else None
        port_out_id = ppr_out_iface.get("ID") if ppr_out_iface is not None else None
        ppr_attrs = []
        for attr in elem.findall("caex:Attribute", ns):
            value_elem= attr.find("caex:Value",ns)
            value = value_elem.text.strip() if value_elem is not None and value_elem.text else None
            ppr_attrs.append({
                "attr_name": attr.get("Name"),
                "data_type": attr.get("AttributeDataType"),
                "value": value
                })

        elements[elem_name] = {
            "name": elem_name,
            "id": elem_id,
            "class": elem_class,
            "xml": elem,
            "port_in_id": port_in_id,
            "port_out_id": port_out_id,
            "parent": parent_name,
            "attributes": ppr_attrs
        }

        for child in elem.findall("caex:InternalElement", ns):
            extract_elements(child, elem_name)

    # Start recursion
    for top_elem in root.findall(".//caex:InstanceHierarchy/caex:InternalElement", ns):
        extract_elements(top_elem)

    return elements

def extract_links(root, ns):

    link_list=[]
    # Step 1: Build lookup for ExternalInterfaces (PPR_out type) by ID just for cardinality
    interface_map = {}
    for ei in root.findall(".//caex:ExternalInterface[@Name='PPR_out']", ns):
        interface_id = ei.get("ID")
        interface_map[interface_id] = ei
    
    # Step 2: Process links
    for elem in root.findall(".//caex:InternalElement",ns):
        for il in elem.findall("caex:InternalLink",ns):
            il_name = il.get("Name")
            il_source = il.get("RefPartnerSideA")
            il_target = il.get("RefPartnerSideB")
            cardinality = None

            # Step 3: Find corresponding ExternalInterface
            ei= interface_map.get(il_source)
            if ei is not None:
                for attr in ei.findall("caex:Attribute", ns):
                    if attr.get("Name") == "cardinality":
                        value_elem = attr.find("caex:Value", ns)
                        if value_elem is not None:
                            cardinality = value_elem.text              
            link_list.append({"name": il_name, "source": il_source, "target": il_target, "cardinality": cardinality})
    return link_list

def iface_mapping(root, ns):
    iface_mapping_dict = {}
    #Assuming that the PPR model has only PPR ports as external interfaces.
    # If there are other types of interfaces, additional filtering logic may be needed here to only include PPR ports in the mapping.
    for elem in root.findall(".//caex:InternalElement", ns):
        elem_name = elem.get("Name")
        if elem_name:
            elem_name = " ".join(elem_name.strip().split()) 
            elem_name = elem_name[0].upper() + elem_name[1:]

        for iface in elem.findall(".//caex:ExternalInterface", ns):
            iface_id = iface.get("ID")
            iface_mapping_dict[iface_id] = elem_name

    return iface_mapping_dict


def extract_ppr_links(link_list:list, iface_mapping_dict:dict, elements:dict):
    ppr_links = []
    for link in link_list:
        source_iface_id = link["source"]
        target_iface_id = link["target"]

        source_elem = iface_mapping_dict.get(source_iface_id)
        target_elem = iface_mapping_dict.get(target_iface_id)

        if source_elem and target_elem:
            parent_child= False
            parent_of_target= elements[target_elem]["parent"]
            if source_elem == parent_of_target:
                parent_child= True
            ppr_links.append({
                "name": source_elem + "_to_" + target_elem,  # You can customize the naming convention as needed
                "source": source_elem,
                "target": target_elem,
                "type": config_data.edgeType_by_view["PPR View"][0],  # Assuming all links extracted here are PPR links. Adjust if there are different types of links.
                "cardinality": link.get("cardinality"),
                "parent_child" : parent_child
            })

    return ppr_links