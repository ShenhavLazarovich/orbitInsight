import streamlit as st
import json
import os
from typing import Dict, List, Any

class DashboardLayout:
    def __init__(self):
        self.layouts_dir = "user_layouts"
        os.makedirs(self.layouts_dir, exist_ok=True)
        
    def save_layout(self, name: str, layout_config: Dict[str, Any]) -> bool:
        """Save a custom dashboard layout configuration"""
        try:
            filepath = os.path.join(self.layouts_dir, f"{name}.json")
            with open(filepath, 'w') as f:
                json.dump(layout_config, f)
            return True
        except Exception as e:
            st.error(f"Failed to save layout: {str(e)}")
            return False
            
    def load_layout(self, name: str) -> Dict[str, Any]:
        """Load a saved dashboard layout configuration"""
        try:
            filepath = os.path.join(self.layouts_dir, f"{name}.json")
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Failed to load layout: {str(e)}")
            return {}
            
    def list_layouts(self) -> List[str]:
        """List all saved dashboard layouts"""
        try:
            layouts = [f[:-5] for f in os.listdir(self.layouts_dir) if f.endswith('.json')]
            return layouts
        except Exception:
            return []
            
    def delete_layout(self, name: str) -> bool:
        """Delete a saved dashboard layout"""
        try:
            filepath = os.path.join(self.layouts_dir, f"{name}.json")
            os.remove(filepath)
            return True
        except Exception:
            return False

def render_layout_manager():
    """Render the layout management interface"""
    st.sidebar.markdown("### Dashboard Layout")
    
    # Initialize layout manager
    layout_manager = DashboardLayout()
    
    # Get saved layouts
    saved_layouts = layout_manager.list_layouts()
    
    # Layout selection
    if saved_layouts:
        selected_layout = st.sidebar.selectbox(
            "Select Layout",
            ["Default"] + saved_layouts
        )
    else:
        selected_layout = "Default"
        
    # Save new layout
    with st.sidebar.expander("Save Current Layout"):
        new_layout_name = st.text_input("Layout Name")
        if st.button("Save Layout") and new_layout_name:
            # Get current layout configuration
            layout_config = {
                "sidebar_state": st.session_state.get("sidebar_state", {}),
                "selected_visualizations": st.session_state.get("selected_visualizations", []),
                "filter_settings": st.session_state.get("filter_settings", {}),
                "custom_colors": st.session_state.get("custom_colors", {}),
                "point_settings": st.session_state.get("point_settings", {})
            }
            if layout_manager.save_layout(new_layout_name, layout_config):
                st.success(f"Layout '{new_layout_name}' saved successfully!")
                
    # Delete layout
    if saved_layouts:
        with st.sidebar.expander("Delete Layout"):
            layout_to_delete = st.selectbox(
                "Select Layout to Delete",
                saved_layouts
            )
            if st.button("Delete") and layout_to_delete:
                if layout_manager.delete_layout(layout_to_delete):
                    st.success(f"Layout '{layout_to_delete}' deleted successfully!")
                    
    return selected_layout

def apply_layout(layout_name: str):
    """Apply a selected layout configuration"""
    if layout_name == "Default":
        return
        
    layout_manager = DashboardLayout()
    layout_config = layout_manager.load_layout(layout_name)
    
    if layout_config:
        # Apply layout settings to session state
        st.session_state.sidebar_state = layout_config.get("sidebar_state", {})
        st.session_state.selected_visualizations = layout_config.get("selected_visualizations", [])
        st.session_state.filter_settings = layout_config.get("filter_settings", {})
        st.session_state.custom_colors = layout_config.get("custom_colors", {})
        st.session_state.point_settings = layout_config.get("point_settings", {}) 