import matplotlib.pyplot as plt
from io import BytesIO

def create_line_graph( x: list, y: list, title: str, x_label: str, y_label: str, line_color: str = "k", line_style: str = "-", marker: str = "o", grid: bool = True) -> BytesIO:
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
