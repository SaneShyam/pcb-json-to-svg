import json
import sys
from pathlib import Path
from html import escape
from itertools import permutations
from math import dist


folder = Path(__file__).parent

TRACE_COLORS: dict[str, str] = {
    "power": "red",
    "ground": "blue",
    "signal": "green"
}


def load_circuit(input_path: Path) -> dict:
    with input_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_components(circuit: dict) -> None:
    if not isinstance(circuit, dict):
        raise ValueError("Circuit must be a JSON object.")

    if "components" not in circuit:
        raise ValueError("Circuit must contain components.")

    components = circuit["components"]

    if not isinstance(components, list) or not components:
        raise ValueError("Components must be a non-empty list.")

    for component in components:
        if not isinstance(component, dict):
            raise ValueError("Each component must be a JSON object.")

        for field in ["name", "type", "value"]:
            if field not in component:
                raise ValueError(f"Component is missing: {field}")

            if not isinstance(component[field], str):
                raise ValueError(f"Component {field} must be text.")

            if not component[field].strip():
                raise ValueError(f"Component {field} cannot be empty.")


def place_components(circuit: dict) -> None:
    column = 0
    y = 60

    for component in circuit["components"]:
        component["x"] = 60 + column * 150
        component["y"] = y

        column = column + 1

        if column == 3:
            column = 0
            y = y + 120


def layout_score(centers: dict, connections: list) -> float:
    total = 0.0

    for link in connections:
        start = centers[link["from"]]
        end = centers[link["to"]]
        total += dist(start, end)

    return total


def choose_layout(centers: dict, connections: list) -> dict:
    if len(centers) > 7 or not connections:
        return centers

    best = centers
    best_score = layout_score(centers, connections)
    names = list(centers)

    for slots in permutations(centers.values()):
        candidate = dict(zip(names, slots))
        score = layout_score(candidate, connections)

        if score < best_score:
            best = candidate
            best_score = score

    return best


def make_svg(circuit: dict) -> str:
    components = circuit["components"]
    width = 120 + min(3, len(components)) * 150
    height = components[-1]["y"] + 140

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
    ]

    # Board outline, four mounting holes and a size label.
    svg_parts.append(
        f'<rect x="10" y="10" width="{width - 20}" height="{height - 20}" rx="12" '
        'fill="#d7ead7" stroke="#1b5e20" stroke-width="3"/>'
    )

    for hole_x in (28, width - 28):
        for hole_y in (28, height - 28):
            svg_parts.append(
                f'<circle cx="{hole_x}" cy="{hole_y}" r="6" fill="white" stroke="black"/>'
            )

    svg_parts.append(
        f'<text x="50" y="33" font-size="11">Board outline {width - 20} x '
        f'{height - 20} px (not to scale)</text>'
    )

    centers = {}

    for component in components:
        name = component["name"]

        if name in centers:
            raise ValueError(f"Duplicate component name: {name}")

        centers[name] = (component["x"] + 30, component["y"] + 15)

    connections = circuit.get("connections")

    if not isinstance(connections, list):
        raise ValueError("Connections must be a list.")

    for connection in connections:
        if not isinstance(connection, dict):
            raise ValueError("Each connection must be a JSON object.")

        source = connection.get("from")
        target = connection.get("to")

        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError('Each connection needs text fields "from" and "to".')

        if source not in centers:
            raise ValueError(f"Unknown source component: {source}")

        if target not in centers:
            raise ValueError(f"Unknown destination component: {target}")

        net = connection.get("net", "signal")

        if net not in TRACE_COLORS:
            raise ValueError(f"Unknown net type: {net}")

    print("Score before search:", round(layout_score(centers, connections), 1))
    centers = choose_layout(centers, connections)
    print("Score after search:", round(layout_score(centers, connections), 1))

    # Traces are coloured by net type and drawn with right-angle segments.
    for connection in connections:
        x1, y1 = centers[connection["from"]]
        x2, y2 = centers[connection["to"]]
        color = TRACE_COLORS[connection.get("net", "signal")]

        if y1 == y2:
            points = f"{x1},{y1} {x2},{y2}"
        else:
            side = -1 if x1 <= x2 else 1
            channel_x = x2 + side * 45
            points = f"{x1},{y1} {channel_x},{y1} {channel_x},{y2} {x2},{y2}"

        svg_parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>'
        )

    for component in components:
        name = component["name"]
        center_x, center_y = centers[name]
        x = center_x - 30
        y = center_y - 15
        details = component["type"] + ": " + component["value"]

        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="60" height="30" '
            'fill="lightblue" stroke="black"/>'
        )

        svg_parts.append(
            f'<text x="{x}" y="{y + 50}" font-size="16">{escape(name)}</text>'
        )

        svg_parts.append(
            f'<text x="{x}" y="{y + 70}" font-size="12">{escape(details)}</text>'
        )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# Optional argument: the input file name. Default is circuit.json.
input_name = sys.argv[1] if len(sys.argv) > 1 else "circuit.json"

circuit = load_circuit(folder / input_name)
validate_components(circuit)
place_components(circuit)

output_path = folder / (Path(input_name).stem + ".svg")
output_path.write_text(make_svg(circuit), encoding="utf-8")

print("Drawing saved to:", output_path)