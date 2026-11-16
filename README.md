# PCB schematic to 2D drawing

Shyam · Task 3, Option B

This offline Python prototype turns a JSON circuit into a labelled SVG drawing. Each component occupies one grid position. Lines show the connections listed in the input.

## Run on Windows

Use Python 3.11 or later. The script uses the Python standard library. Place `pcb_to_svg.py` and the four JSON files in the same folder, then open PowerShell in that folder.

```powershell
python .\pcb_to_svg.py
start .\circuit.svg
```

The first command reads the default input, `circuit.json`, prints the placement scores, and saves the SVG beside the script. The second opens the drawing. To run another example, pass its filename:

```powershell
python .\pcb_to_svg.py resistor_led.json
python .\pcb_to_svg.py led_supply.json
python .\pcb_to_svg.py dual_led_indicator.json
```

Each SVG uses its input's base name. Running an example again updates its SVG.

| Input | Output | Parts | Placement score before → after (px) |
| --- | --- | ---: | ---: |
| circuit.json | circuit.svg | 5 | 642.1 → 540.0 |
| resistor_led.json | resistor_led.svg | 2 | 150.0 → 150.0 |
| led_supply.json | led_supply.svg | 4 | 623.1 → 420.0 |
| dual_led_indicator.json | dual_led_indicator.svg | 8 | 1273.0 → 1273.0 |

## Input format

The JSON object contains a non-empty `components` list and a `connections` list. Each component has a unique `name` and non-empty text fields `type` and `value`. Each connection names two existing components using `from` and `to`. The optional `net` label sets the line colour. Power is red, ground is blue, and signal is green. Omitting `net` selects signal. See `resistor_led.json` for the smallest complete example.

## Placement and drawing

The script first places components in input order on a three-column grid. It scores a layout by adding the straight-line distances between the centres of connected components. For up to seven components with connections, it tries every assignment to the occupied grid positions and keeps the lowest score. For larger inputs it keeps the initial layout because the number of assignments grows factorially. The switched LED example reduces the score by 15.9%. The eight-component example demonstrates the fallback.

## Assumptions, limitations and next steps

The drawing represents component-level connections with simplified boxes and traces. The score measures proximity in drawing pixels. Actual routed paths can bend, overlap or cross, as the dual LED example shows. The board outline is illustrative. The validator checks fields, unique names and connection references. Electrical correctness and individual pins are outside its scope.

With more time, I would add named pins and check for overlapping trace segments so that separate connections are easier to follow.
