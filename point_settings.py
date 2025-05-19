import streamlit as st
from typing import Dict, Any, Tuple
import numpy as np
import colorsys

class PointVisualizationSettings:
    def __init__(self):
        self.default_settings = {
            "point_size": 4,
            "min_point_size": 1,
            "max_point_size": 10,
            "opacity": 0.8,
            "min_opacity": 0.1,
            "max_opacity": 1.0,
            "color_start": "#115F9A",  # Deep blue
            "color_end": "#E6E9EB",    # Almost white
            "density_threshold": 100,   # Points per area unit
            "clustering_enabled": True,
            "show_labels": False,
            "label_size": 10,
            "highlight_anomalies": True,
            "anomaly_color": "#FF4B4B"  # Red
        }
        
    def generate_color_gradient(self, num_points: int) -> list:
        """Generate a color gradient from start to end color"""
        def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))
        
        def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
            return '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        
        start_rgb = hex_to_rgb(self.default_settings["color_start"])
        end_rgb = hex_to_rgb(self.default_settings["color_end"])
        
        colors = []
        for i in range(num_points):
            t = i / (num_points - 1)
            r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t
            g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t
            b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t
            colors.append(rgb_to_hex((r, g, b)))
            
        return colors
        
    def adjust_point_density(self, points: np.ndarray, 
                           max_points: int = 1000) -> np.ndarray:
        """Adjust point density based on settings"""
        if len(points) <= max_points:
            return points
            
        if self.default_settings["clustering_enabled"]:
            # Use simple clustering by taking every nth point
            n = len(points) // max_points
            return points[::n]
        else:
            # Random sampling
            indices = np.random.choice(
                len(points), max_points, replace=False)
            return points[indices]
            
    def render_settings_ui(self):
        """Render the point visualization settings UI"""
        st.sidebar.markdown("### Point Visualization Settings")
        
        with st.sidebar.expander("Point Appearance"):
            self.default_settings["point_size"] = st.slider(
                "Point Size",
                min_value=self.default_settings["min_point_size"],
                max_value=self.default_settings["max_point_size"],
                value=self.default_settings["point_size"]
            )
            
            self.default_settings["opacity"] = st.slider(
                "Opacity",
                min_value=self.default_settings["min_opacity"],
                max_value=self.default_settings["max_opacity"],
                value=self.default_settings["opacity"]
            )
            
            self.default_settings["color_start"] = st.color_picker(
                "Start Color",
                self.default_settings["color_start"]
            )
            
            self.default_settings["color_end"] = st.color_picker(
                "End Color",
                self.default_settings["color_end"]
            )
            
        with st.sidebar.expander("Density Controls"):
            self.default_settings["clustering_enabled"] = st.checkbox(
                "Enable Point Clustering",
                value=self.default_settings["clustering_enabled"]
            )
            
            self.default_settings["density_threshold"] = st.slider(
                "Density Threshold",
                min_value=10,
                max_value=500,
                value=self.default_settings["density_threshold"]
            )
            
        with st.sidebar.expander("Labels & Highlights"):
            self.default_settings["show_labels"] = st.checkbox(
                "Show Point Labels",
                value=self.default_settings["show_labels"]
            )
            
            if self.default_settings["show_labels"]:
                self.default_settings["label_size"] = st.slider(
                    "Label Size",
                    min_value=8,
                    max_value=16,
                    value=self.default_settings["label_size"]
                )
                
            self.default_settings["highlight_anomalies"] = st.checkbox(
                "Highlight Anomalies",
                value=self.default_settings["highlight_anomalies"]
            )
            
            if self.default_settings["highlight_anomalies"]:
                self.default_settings["anomaly_color"] = st.color_picker(
                    "Anomaly Color",
                    self.default_settings["anomaly_color"]
                )
                
        return self.default_settings
        
    def apply_settings_to_figure(self, fig, points: np.ndarray):
        """Apply current settings to a plotly figure"""
        settings = self.default_settings
        
        # Adjust point density if needed
        adjusted_points = self.adjust_point_density(
            points, settings["density_threshold"])
        
        # Generate color gradient
        colors = self.generate_color_gradient(len(adjusted_points))
        
        # Update marker properties
        for trace in fig.data:
            if hasattr(trace, 'marker'):
                trace.marker.update(
                    size=settings["point_size"],
                    opacity=settings["opacity"],
                    color=colors
                )
                
            if settings["show_labels"]:
                trace.textfont.size = settings["label_size"]
                trace.mode = 'markers+text'
            else:
                trace.mode = 'markers'
                
        return fig 