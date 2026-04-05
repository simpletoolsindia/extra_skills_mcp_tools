"""Matplotlib MCP - Generate charts and visualizations from data."""

from __future__ import annotations

import os
import json
import base64
from io import BytesIO
from typing import Optional, List, Dict, Any, Union

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False


# Default style
DEFAULT_STYLE = os.environ.get("MPL_STYLE", "seaborn-v0_8-darkgrid")


def _setup_plot(style: Optional[str] = None) -> None:
    """Setup matplotlib style."""
    if MPL_AVAILABLE and style:
        try:
            plt.style.use(style)
        except:
            pass


def _to_base64(fig) -> str:
    """Convert figure to base64 PNG."""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def _to_html(fig) -> str:
    """Convert figure to base64 HTML img."""
    img_data = _to_base64(fig)
    return f'<img src="data:image/png;base64,{img_data}" />'


def plot_line(
    x: List[Union[int, float]],
    y: List[Union[int, float]],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    labels: Optional[List[str]] = None,
    style: Optional[str] = None,
    width: int = 10,
    height: int = 6,
) -> dict:
    """
    Create a line plot.

    Args:
        x: X-axis data (list of values or list of lists for multiple lines)
        y: Y-axis data (list of values or list of lists for multiple lines)
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        labels: Legend labels for multiple lines
        style: Matplotlib style
        width: Figure width
        height: Figure height

    Returns:
        dict with keys: base64_image, html, error
    """
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed. pip install matplotlib"}

    try:
        _setup_plot(style)
        fig, ax = plt.subplots(figsize=(width, height))

        # Handle multiple lines
        if isinstance(y[0], list):
            for i, y_data in enumerate(y):
                label = labels[i] if labels and i < len(labels) else f"Line {i+1}"
                ax.plot(x if isinstance(x[0], (int, float)) else range(len(x)), y_data, label=label)
            if labels:
                ax.legend()
        else:
            ax.plot(x, y)

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return {
            "base64_image": _to_base64(fig),
            "html": _to_html(fig),
            "error": None,
        }
    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}
    finally:
        plt.close('all')


def plot_bar(
    categories: List[str],
    values: List[Union[int, float]],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    horizontal: bool = False,
    color: str = "#3498db",
    style: Optional[str] = None,
    width: int = 10,
    height: int = 6,
) -> dict:
    """Create a bar chart."""
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed"}

    try:
        _setup_plot(style)
        fig, ax = plt.subplots(figsize=(width, height))

        if horizontal:
            ax.barh(categories, values, color=color)
            if xlabel:
                ax.set_xlabel(xlabel)
        else:
            ax.bar(categories, values, color=color)
            if ylabel:
                ax.set_ylabel(ylabel)

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')

        plt.xticks(rotation=45 if not horizontal else 0, ha='right')
        ax.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()

        return {
            "base64_image": _to_base64(fig),
            "html": _to_html(fig),
            "error": None,
        }
    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}
    finally:
        plt.close('all')


def plot_pie(
    labels: List[str],
    values: List[Union[int, float]],
    title: str = "",
    colors: Optional[List[str]] = None,
    explode: Optional[List[float]] = None,
    style: Optional[str] = None,
    size: int = 8,
) -> dict:
    """Create a pie chart."""
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed"}

    try:
        _setup_plot(style)
        fig, ax = plt.subplots(figsize=(size, size))

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            explode=explode,
            shadow=True,
        )

        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()

        return {
            "base64_image": _to_base64(fig),
            "html": _to_html(fig),
            "error": None,
        }
    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}
    finally:
        plt.close('all')


def plot_scatter(
    x: List[Union[int, float]],
    y: List[Union[int, float]],
    sizes: Optional[List[float]] = None,
    colors: Optional[List[Union[int, str]]] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    style: Optional[str] = None,
    width: int = 10,
    height: int = 6,
) -> dict:
    """Create a scatter plot."""
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed"}

    try:
        _setup_plot(style)
        fig, ax = plt.subplots(figsize=(width, height))

        # Handle multiple datasets
        if isinstance(x[0], list):
            for i, (x_data, y_data) in enumerate(zip(x, y)):
                size_data = sizes[i] if sizes and i < len(sizes) else None
                color_data = colors[i] if colors and i < len(colors) else None
                ax.scatter(x_data, y_data, s=size_data, c=color_data, alpha=0.7)
        else:
            ax.scatter(x, y, s=sizes, c=colors, alpha=0.7)

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return {
            "base64_image": _to_base64(fig),
            "html": _to_html(fig),
            "error": None,
        }
    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}
    finally:
        plt.close('all')


def plot_histogram(
    data: List[Union[int, float]],
    bins: int = 30,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "Frequency",
    color: str = "#3498db",
    style: Optional[str] = None,
    width: int = 10,
    height: int = 6,
) -> dict:
    """Create a histogram."""
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed"}

    try:
        _setup_plot(style)
        fig, ax = plt.subplots(figsize=(width, height))

        ax.hist(data, bins=bins, color=color, edgecolor='white', alpha=0.8)

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()

        return {
            "base64_image": _to_base64(fig),
            "html": _to_html(fig),
            "error": None,
        }
    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}
    finally:
        plt.close('all')


def plot_box(data: List[List[Union[int, float]]], labels: Optional[List[str]] = None,
             title: str = "", style: Optional[str] = None, width: int = 10, height: int = 6) -> dict:
    """Create a box plot."""
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed"}

    try:
        _setup_plot(style)
        fig, ax = plt.subplots(figsize=(width, height))
        bp = ax.boxplot(data, labels=labels, patch_artist=True)

        for patch in bp['boxes']:
            patch.set_facecolor('#3498db')
            patch.set_alpha(0.7)

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')

        ax.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()

        return {
            "base64_image": _to_base64(fig),
            "html": _to_html(fig),
            "error": None,
        }
    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}
    finally:
        plt.close('all')


def create_subplots(
    plots: List[dict],
    rows: int = 2,
    cols: int = 2,
    title: str = "",
    width: int = 12,
    height: int = 10,
) -> dict:
    """
    Create multiple subplots.

    plots: List of dict with keys: type (line/bar/pie/scatter/hist), x, y, title, etc.
    """
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed"}

    try:
        fig, axes = plt.subplots(rows, cols, figsize=(width, height))
        if rows == 1 and cols == 1:
            axes = [[axes]]
        elif rows == 1 or cols == 1:
            axes = axes.reshape(rows, cols)

        for i, plot_config in enumerate(plots[:rows * cols]):
            row, col = i // cols, i % cols
            ax = axes[row][col]

            plot_type = plot_config.get("type", "line")

            if plot_type == "line":
                ax.plot(plot_config.get("x", []), plot_config.get("y", []))
            elif plot_type == "bar":
                ax.bar(plot_config.get("categories", []), plot_config.get("values", []),
                       color=plot_config.get("color", "#3498db"))
            elif plot_type == "scatter":
                ax.scatter(plot_config.get("x", []), plot_config.get("y", []))

            if plot_config.get("title"):
                ax.set_title(plot_config["title"])
            if plot_config.get("xlabel"):
                ax.set_xlabel(plot_config["xlabel"])
            if plot_config.get("ylabel"):
                ax.set_ylabel(plot_config["ylabel"])

            ax.grid(True, alpha=0.3)

        if title:
            fig.suptitle(title, fontsize=16, fontweight='bold')

        plt.tight_layout()

        return {
            "base64_image": _to_base64(fig),
            "html": _to_html(fig),
            "error": None,
        }
    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}
    finally:
        plt.close('all')


def render_markdown_chart(chart_md: str) -> dict:
    """
    Render a chart from Markdown-like syntax.

    Supports:
    ```chart
    type: line
    title: My Chart
    x: [1, 2, 3, 4, 5]
    y: [10, 20, 15, 25, 30]
    ```
    """
    if not MPL_AVAILABLE:
        return {"base64_image": "", "html": "", "error": "matplotlib not installed"}

    import re

    chart_block = re.search(r'```chart\s*\n(.*?)```', chart_md, re.DOTALL)
    if not chart_block:
        return {"base64_image": "", "html": "", "error": "No chart block found. Use ```chart ... ``` syntax"}

    try:
        config_str = chart_block.group(1)
        config = {}

        for line in config_str.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse values
                if value.startswith('['):
                    config[key] = json.loads(value)
                elif value.replace('.', '').replace('-', '').isdigit():
                    config[key] = float(value) if '.' in value else int(value)
                elif value in ['true', 'false']:
                    config[key] = value == 'true'
                else:
                    config[key] = value

        chart_type = config.get('type', 'line')

        if chart_type == 'line':
            return plot_line(config.get('x', []), config.get('y', []),
                             title=config.get('title', ''),
                             xlabel=config.get('xlabel', ''),
                             ylabel=config.get('ylabel', ''))
        elif chart_type == 'bar':
            return plot_bar(config.get('categories', []), config.get('values', []),
                            title=config.get('title', ''),
                            xlabel=config.get('xlabel', ''),
                            ylabel=config.get('ylabel', ''))
        elif chart_type == 'pie':
            return plot_pie(config.get('labels', []), config.get('values', []),
                            title=config.get('title', ''))
        elif chart_type == 'scatter':
            return plot_scatter(config.get('x', []), config.get('y', []),
                                title=config.get('title', ''),
                                xlabel=config.get('xlabel', ''),
                                ylabel=config.get('ylabel', ''))
        elif chart_type == 'hist':
            return plot_histogram(config.get('data', []),
                                  title=config.get('title', ''),
                                  xlabel=config.get('xlabel', ''))

        return {"base64_image": "", "html": "", "error": f"Unknown chart type: {chart_type}"}

    except Exception as e:
        return {"base64_image": "", "html": "", "error": str(e)}