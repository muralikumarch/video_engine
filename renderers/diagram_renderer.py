import os
import graphviz
from PIL import Image, ImageDraw, ImageFont

# Automatically append standard Graphviz install paths to PATH on Windows if present
for path in [r"C:\Program Files\Graphviz\bin", r"C:\Program Files (x86)\Graphviz\bin"]:
    if os.path.exists(path) and path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + path


def render_diagram(data, output_path, theme):
    bg = tuple(theme.get("bg_color", [20, 24, 33]))
    accent = tuple(theme.get("accent_color", [56, 189, 248]))
    card = tuple(theme.get("card_color", [30, 36, 50]))
    text_main = tuple(theme.get("text_main", [240, 244, 250]))

    try:
        dot = graphviz.Digraph(comment=data.get("title", "Architecture"), format="png")
        dot.attr(bgcolor="#141821", rankdir=data.get("layout", "LR"), size="16,9!")
        dot.attr(
            "node",
            shape="box",
            style="filled",
            fontname="Segoe UI, Arial",
            fontsize="12",
            fontcolor="#ffffff",
        )
        dot.attr("edge", color="#38bdf8", fontcolor="#9ca3af", fontsize="10")

        # Clusters / Subgraphs
        for cluster in data.get("clusters", []):
            with dot.subgraph(name=cluster["name"]) as c:
                c.attr(label=cluster.get("label", ""), color="#38bdf8", fontcolor="#38bdf8")
                for node in cluster.get("nodes", []):
                    c.node(
                        node["id"],
                        node["label"],
                        fillcolor=node.get("color", "#1e293b"),
                        shape=node.get("shape", "box"),
                    )

        # Standalone Nodes
        for node in data.get("standalone_nodes", []):
            dot.node(
                node["id"],
                node["label"],
                fillcolor=node.get("color", "#0f766e"),
                shape=node.get("shape", "box"),
            )

        # Edges
        for edge in data.get("edges", []):
            dot.edge(edge["from"], edge["to"], label=edge.get("label", ""))

        temp_base = output_path.replace(".png", "")
        rendered_file = dot.render(temp_base, cleanup=True)

        # Normalize to 1920x1080 canvas
        raw_img = Image.open(rendered_file)
        final_canvas = Image.new("RGB", (1920, 1080), bg)

        # Scale image to fit within canvas maintaining aspect ratio
        raw_img.thumbnail((1800, 1000), Image.Resampling.LANCZOS)
        x = (1920 - raw_img.width) // 2
        y = (1080 - raw_img.height) // 2
        final_canvas.paste(raw_img, (x, y))
        final_canvas.save(output_path, "PNG")

        if os.path.exists(rendered_file) and rendered_file != output_path:
            os.remove(rendered_file)
    except Exception as err:
        print(f"[Warning] Graphviz rendering failed ({err}). Using PIL fallback.")
        img = Image.new("RGB", (1920, 1080), bg)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((80, 60), data.get("title", "Architecture Diagram"), fill=accent, font=font)
        y = 150
        for cluster in data.get("clusters", []):
            draw.text((100, y), cluster.get("label", ""), fill=accent, font=font)
            y += 30
            for node in cluster.get("nodes", []):
                draw.rectangle([(120, y), (500, y + 40)], fill=card)
                draw.text((130, y + 10), node.get("label", node["id"]), fill=text_main, font=font)
                y += 50
        img.save(output_path, "PNG")

