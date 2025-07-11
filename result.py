from inputs import get_input
from collections import defaultdict
from tabulate import tabulate

def show_custom_results(data_list, headers, row_builder_fn, title=None):
    from tabulate import tabulate
    if title:
        print(f"\n{title}\n{'-' * len(title)}")
    table = [row_builder_fn(item) for item in data_list]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num):
    while True:
        quantity = get_input("Enter quantity of bars: ", int, allow_back=True)
        if quantity == "BACK":
            return "BACK"
        total_len = quantity * length
        ld = 46 * d
        results.append({
            "type": "Top beam" if choice == "1" else "Bottom beam" if choice == "2" else "Cantilever",
            "beam no.": beam_num,
            "d": d,
            "clear span": clear_span,
            "bend length1": bl1,
            "bend length2": bl2,
            "quantity": quantity,
            "ld": ld,
            "length per bar": length,
        })
        print(f"Cutting length per bar: {length:.2f}")
        print(f"Total length for {quantity} bars: {total_len:.2f}")
        return
    
"""
def seg_by_d(results):
    summary = defaultdict(list)
    for entry in results:
        summary[entry["diameter"]].append(entry)

    for d, entries in summary.items():
        headers = ["Beam No.", "Clear Span", "Type", "Bend Len1", "Bend Len2", "Qty", "Cutting Length"]
        show_custom_results(
            entries,
            headers,
            lambda e: [
                e["beam no."], e["clear span"], e["type"],
                e["bend length1"], e["bend length2"], e["quantity"],
                f"{e['length per bar']:.2f}"
            ],
            title=f"Bar Diameter: {d}"
        )
"""

def group_by_field(data, group_key, field_order, field_names=None, title_prefix=None):
    """
    Groups data by a specific field and prints separate tables.

    Parameters:
        data (list[dict]): The data to display.
        group_key (str): The key to group by (e.g., "diameter").
        field_order (list[str]): Keys in the order you want to display.
        field_names (list[str], optional): Display names for headers.
        title_prefix (str, optional): Prefix for section titles like "Bar diameter: "

    """
    grouped = defaultdict(list)
    for entry in data:
        grouped[entry[group_key]].append(entry)

    for key_val, entries in grouped.items():
        title = f"\n{title_prefix or group_key.title()}: {key_val}"
        print(title)
        headers = field_names if field_names else [k.replace("_", " ").title() for k in field_order]
        table = []
        for e in entries:
            row = []
            for key in field_order:
                val = e.get(key, "")
                if isinstance(val, float):
                    val = f"{val:.2f}"
                row.append(val)
            table.append(row)
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
