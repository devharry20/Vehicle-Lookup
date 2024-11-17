import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO

def create_line_graph(x: list, y: list, title: str, x_label: str = "", y_label: str = "", line_color: str = "k", line_style: str = "-", marker: str = "", grid: bool = True) -> BytesIO:
    buffer = BytesIO()

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker=marker, color=line_color, linestyle=line_style, linewidth=2, markersize=6)
    plt.title(title)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if grid:
        plt.grid(True, axis="x")
    
    plt.savefig(buffer, format="PNG", dpi=150)
    buffer.seek(0)
    plt.close()

    return buffer

def create_stacked_bar_graph(x: list, y1: list, y2: list, colours: list = ["#ff571a", "#ff0000"], title: str = "", x_label: str = "", y_label: str = "") -> BytesIO:
    buffer = BytesIO()
    
    plt.figure(figsize = (8, 5))

    plt.bar(x, y1, color=colours[0], width=0.3)
    plt.bar(x, y2, color=colours[1], width=0.3)

    advisories_patch = mpatches.Patch(color=colours[0], label="Advisories")
    majors_patch = mpatches.Patch(color=colours[1], label="Majors")

    plt.legend(handles=[advisories_patch, majors_patch])

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(buffer, format="PNG", dpi=150)

    buffer.seek(0)
    plt.close()

    return buffer
