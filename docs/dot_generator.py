def generate_dot(flow_items):
    dot_str = 'digraph flowchart {\n'
    for item in flow_items:
        dot_str += f'    {item["id"]} [label="{item["label"]}", shape={item["shape"]}];\n'
        for target in item.get("targets", []):
            dot_str += f'    {item["id"]} -> {target};\n'
    dot_str += '}'
    return dot_str

flow_items = [
    {"id": "start", "label": "Start", "shape": "ellipse"},
    {"id": "decision1", "label": "Decision?", "shape": "diamond", "targets": ["operation1", "operation2"]},
    {"id": "operation1", "label": "Operation 1", "shape": "box", "targets": ["end"]},
    {"id": "operation2", "label": "Operation 2", "shape": "box", "targets": ["end"]},
    {"id": "end", "label": "End", "shape": "ellipse"}
]

dot_file_content = generate_dot(flow_items)

with open('flowchart.dot', 'w') as file:
    file.write(dot_file_content)
