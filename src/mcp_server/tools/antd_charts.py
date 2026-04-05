"""Antd-style chart generation for React-style dashboards."""

from __future__ import annotations

import json
from typing import Optional, List, Dict, Any


def generate_line_chart(
    data: List[Dict],
    x_field: str = "x",
    y_field: str = "y",
    series_field: Optional[str] = None,
    title: str = "",
    height: int = 400,
) -> dict:
    """
    Generate line chart spec for Ant Design Charts.

    Args:
        data: List of data points
        x_field: Key for x-axis values
        y_field: Key for y-axis values
        series_field: Key for grouping into multiple lines
        title: Chart title
        height: Chart height in pixels

    Returns:
        dict with Ant Design Charts JSON spec
    """
    spec = {
        "type": "line",
        "data": data,
        "encoding": {
            "x": {"field": x_field, "type": "temporal"},
            "y": {"field": y_field, "type": "quantitative"},
        },
        "height": height,
    }

    if series_field:
        spec["encoding"]["color"] = {"field": series_field, "type": "nominal"}

    if title:
        spec["title"] = {"text": title, "subTitle": ""}

    return {"spec": spec, "format": "antd-charts", "error": None}


def generate_bar_chart(
    data: List[Dict],
    x_field: str,
    y_field: str,
    series_field: Optional[str] = None,
    title: str = "",
    horizontal: bool = False,
    height: int = 400,
) -> dict:
    """Generate bar chart spec."""
    spec = {
        "type": "interval",
        "data": data,
        "encoding": {
            "x": {"field": x_field, "type": "nominal" if horizontal else "temporal"},
            "y": {"field": y_field, "type": "quantitative"},
        },
        "height": height,
    }

    if horizontal:
        spec["encoding"]["x"]["type"] = "quantitative"
        spec["encoding"]["y"]["type"] = "nominal"

    if series_field:
        spec["encoding"]["color"] = {"field": series_field, "type": "nominal"}

    if title:
        spec["title"] = {"text": title}

    return {"spec": spec, "format": "antd-charts", "error": None}


def generate_pie_chart(
    data: List[Dict],
    angle_field: str,
    color_field: str,
    title: str = "",
    height: int = 400,
) -> dict:
    """Generate pie/rose chart spec."""
    spec = {
        "type": "interval",
        "data": data,
        "encoding": {
            "theta": {"field": angle_field, "type": "quantitative"},
            "color": {"field": color_field, "type": "nominal"},
        },
        "coordinate": {"type": "polar"},
        "height": height,
    }

    if title:
        spec["title"] = {"text": title}

    return {"spec": spec, "format": "antd-charts", "error": None}


def generate_scatter_chart(
    data: List[Dict],
    x_field: str,
    y_field: str,
    size_field: Optional[str] = None,
    color_field: Optional[str] = None,
    title: str = "",
    height: int = 400,
) -> dict:
    """Generate scatter plot spec."""
    spec = {
        "type": "point",
        "data": data,
        "encoding": {
            "x": {"field": x_field, "type": "quantitative"},
            "y": {"field": y_field, "type": "quantitative"},
        },
        "height": height,
    }

    if size_field:
        spec["encoding"]["size"] = {"field": size_field, "type": "quantitative"}

    if color_field:
        spec["encoding"]["color"] = {"field": color_field, "type": "nominal"}

    if title:
        spec["title"] = {"text": title}

    return {"spec": spec, "format": "antd-charts", "error": None}


def generate_heatmap(
    data: List[Dict],
    x_field: str,
    y_field: str,
    color_field: str,
    title: str = "",
    height: int = 400,
) -> dict:
    """Generate heatmap spec."""
    spec = {
        "type": "rect",
        "data": data,
        "encoding": {
            "x": {"field": x_field, "type": "nominal"},
            "y": {"field": y_field, "type": "nominal"},
            "color": {"field": color_field, "type": "quantitative"},
        },
        "height": height,
    }

    if title:
        spec["title"] = {"text": title}

    return {"spec": spec, "format": "antd-charts", "error": None}


def generate_gauge_chart(
    value: float,
    min: float = 0,
    max: float = 100,
    title: str = "",
    height: int = 300,
) -> dict:
    """Generate gauge chart spec."""
    spec = {
        "type": "arc",
        "data": [{"type": "current", "value": value}, {"type": "remaining", "value": max - value}],
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "type", "type": "nominal", "scale": {"range": ["#1890ff", "#f0f0f0"]}},
        },
        "height": height,
    }

    if title:
        spec["title"] = {"text": title}

    return {"spec": spec, "format": "antd-charts", "error": None}


def generate_dashboard(
    charts: List[Dict],
    title: str = "Dashboard",
    columns: int = 2,
) -> dict:
    """
    Generate multi-chart dashboard spec.

    charts: List of chart specs (each with type, data, encoding, etc.)
    """
    dashboard = {
        "layout": "grid",
        "columns": columns,
        "title": title,
        "charts": charts,
    }

    return {"dashboard": dashboard, "format": "antd-dashboard", "error": None}


def render_html_dashboard(
    dashboard_spec: dict,
    title: str = "MCP Dashboard",
) -> dict:
    """
    Render dashboard as standalone HTML.

    Uses Chart.js for rendering since it's a client-side library.
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; background: #f0f2f5; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .dashboard {{ display: grid; gap: 20px; }}
        .chart-card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .chart-container {{ position: relative; height: 300px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="dashboard" id="dashboard"></div>
    <script>
        const dashboardSpec = {json.dumps(dashboard_spec)};
        const container = document.getElementById('dashboard');
        // Render charts using Chart.js
        // This is a simplified version - full implementation would parse the spec
        document.write('<pre>' + JSON.stringify(dashboardSpec, null, 2) + '</pre>');
    </script>
</body>
</html>"""

    return {"html": html, "error": None}


def create_table(
    data: List[Dict],
    columns: Optional[List[Dict]] = None,
    title: str = "",
    page_size: int = 10,
) -> dict:
    """
    Create Ant Design Table spec.

    columns: List of {title, dataIndex, width, sorter, filterable}
    """
    spec = {
        "type": "table",
        "data": data,
        "pagination": {"pageSize": page_size},
    }

    if columns:
        spec["columns"] = columns

    if title:
        spec["title"] = title

    return {"spec": spec, "format": "antd-table", "error": None}