from inputs import get_input
import math
from result import group_by_field

def menu():
    print("1. One way slab")
    print("2. Two way slab")
    print("3. Exit")

def slab_flow():
    slab_data = []

    while True:
        menu()
        slab_type = input("Enter 1/2/3 as per requirement: ").strip()

        if slab_type == "1":
            x = get_input("Enter breadth of slab (shorter span): ")
            y = get_input("Enter length of slab (longer span): ")
            if y < x:
                print("Invalid values: Length must be greater than or equal to breadth.")
                y = get_input("Enter length of slab (longer span): ")

            a = get_input("Enter adjacent span to x on right side: ")
            b = get_input("Enter adjacent span to x on left side: ")
            beam_width1 = get_input("Enter beam width 1: ")
            beam_width2 = get_input("Enter beam width 2: ")
            d = get_input("Enter the diameter of bar (e.g., 8 or 10): ")
            spacing_mainBar = get_input("Enter spacing between main bars: ")
            spacing_distBar = get_input("Enter spacing between distribution bars: ")

            num_main_bars = math.floor((y / spacing_mainBar) + 1)
            num_dist_bars = math.floor((x / spacing_distBar) + 1)

            #cutting lens :-
            l1 = ((x + beam_width1 + beam_width2 + a / 4)/1000)
            l2 = ((x + beam_width1 + beam_width2 + b / 4)/1000)

            weight1 = math.floor((num_main_bars / 2) * l1)
            weight2 = math.floor((num_main_bars - num_main_bars / 2) * l2)
            total_weight = weight1 + weight2

            slab_data.append({
                "type": "One-way",
                "diameter": d,
                "main bars": num_main_bars,
                "dist bars": num_dist_bars,
                "cutting len1": l1,
                "cutting len2": l2,
                "total weight": total_weight
            })

        elif slab_type == "2":
            print("Two-way slab calculation not yet implemented.")
            continue

        elif slab_type == "3":
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    # Summary:
    field_order = ["type", "diameter", "main bars", "dist bars", "cutting len1", "cutting len2", "total weight"]
    field_names = ["Type", "Diameter", "Main Bars", "Dist Bars", "Cutting Len (L1) m", "Cutting Len (L2) m", "Total Weight (kg)"]

    group_by_field(slab_data, group_key="diameter", field_order=field_order, field_names=field_names)

if __name__ == "__main__":
    slab_flow()
