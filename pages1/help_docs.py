import streamlit as st

def show():
    st.header("❓ Help & Documentation")
    st.markdown("#### ℹ️ About")

    st.markdown("""
    This application enables the creation and visualization of **Product–Process–Resource (PPR)** models.

    You can:
    - Build or import PPR model  
    - Define relationships between Product, Process, and Resource  
    - Explore the model through different viewpoints (Engineering, Sustainability)

    The tool ensures that all models follow valid PPR rules while allowing flexible analysis through multiple viewpoints.
    """)
    st.markdown("#### 📌 Valid PPR Format")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image(
            "valid_ppr_structure.png",
            caption="PPR Meta Model",
            width=450
        )
    st.markdown("""
A valid PPR model consists of three core elements:

- **Product** → the item being created or transformed  
- **Process** → the value-adding activity  
- **Resource** → the means used to perform the process  

Each element can contain child elements.

**Valid Connections** are:
- Product → Process 
- Process → Product               
- Process → Resource  

A Product instance can undergo only **one Process**, and there must be **no direct link between Product and Resource**.
""")

    st.markdown("### 📄 Documentation")

    st.markdown("""
    Access the full system documentation, including:
    - System design overview  
    - PPR model structure  
    - Implementation details  

    Download the complete report below.
    """)

    with open("dummy.pdf", "rb") as file:
        st.download_button(
            label="⬇️ Download Documentation",
            data=file,
            file_name="PPR_Documentation.pdf",
            mime="application/pdf"
        )