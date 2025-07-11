from cuttingLen import flow1, flow2, flow3, flow4, bend_length
from result import theLoop, group_by_field
from inputs import get_input
from stirrups import stirrup_flow
from slab import slab_flow

def menu():
    print("\nCutting Length Calculator for Continuous Bars")
    print("DO NOTE ALL INPUTS/OUTPUTS ARE TO BE IN MM")
    print("1. Top beam")
    print("2. Bottom beam")
    print("3. Cantilever")
    print("4. Stirrups")
    print("5. Slab")
    print("6. Exit") 

def main():
    results = []

    while True:
        menu()
        choice = input("Press 1/2/3 as per requirement: ").strip()
        if choice not in ("1", "2", "3", "4", "5"):
            print("\nThank you for using the software.")
            break

        clear_span = beam_num = beam_depth = 0

        if choice in ("1", "2"):
            while True:
                clear_span = get_input("Enter clear span of beam (in mm): ", allow_back=True)
                if clear_span == "BACK":
                    break
                beam_num = get_input("Enter the beam number: ", int, allow_back=True)
                if beam_num == "BACK":
                    continue
                beam_depth = get_input("Enter beam depth (in mm): ", allow_back=True)
                if beam_depth == "BACK":
                    continue

                end_supp = input("Is end support present? (y/n): ").strip().lower()
                if end_supp == "BACK":
                    continue
                if end_supp == "y":
                    while True:
                        quant_endSupp = get_input("Enter how many end supports present (1 or 2): ", int, allow_back=True)
                        if quant_endSupp == "BACK":
                            break

                        if quant_endSupp == 1:
                            es_width = get_input("Enter the width of end support (in mm): ", allow_back=True)
                            if es_width == "BACK":
                                continue

                            while True:
                                types_bars = get_input("Enter number of bar diameters you want to input: ", int, allow_back=True)
                                if types_bars == "BACK":
                                    break

                                for i in range(types_bars):
                                    d = get_input(f"Enter diameter of bar {i+1} (in mm): ", allow_back=True)
                                    if d == "BACK":
                                        break
                                    bl1 = bend_length(d, es_width)
                                    bl2 = 0
                                    length = flow2(d, clear_span, es_width, beam_depth, bl1)
                                    if theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num) == "BACK":
                                        break
                                break
                            break

                        elif quant_endSupp == 2:
                            es_width1 = get_input("Enter width of end support 1 (in mm): ", allow_back=True)
                            if es_width1 == "BACK":
                                continue
                            es_width2 = get_input("Enter width of end support 2 (in mm): ", allow_back=True)
                            if es_width2 == "BACK":
                                continue

                            while True:
                                types_bars = get_input("Enter number of bar diameters you want to input: ", int, allow_back=True)
                                if types_bars == "BACK":
                                    break
                                for i in range(types_bars):
                                    d = get_input(f"Enter diameter of bar {i+1} (in mm): ", allow_back=True)
                                    if d == "BACK":
                                        break
                                    bl1 = bend_length(d, es_width1)
                                    bl2 = bend_length(d, es_width2)
                                    length = flow1(d, clear_span, es_width1, es_width2, beam_depth, bl1, bl2)
                                    if theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num) == "BACK":
                                        break
                                break
                            break
                        else:
                            print("Enter either 1 or 2.")
                else:
                    while True:
                        types_bars = get_input("Enter number of bar diameters you want to input: ", int, allow_back=True)
                        if types_bars == "BACK":
                            break
                        for i in range(types_bars):
                            d = get_input(f"Enter diameter of bar {i+1} (in mm): ", allow_back=True)
                            if d == "BACK":
                                break
                            bl1 = bl2 = 0
                            length = flow3(d, clear_span)
                            if theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num) == "BACK":
                                break
                        break
                break

        elif choice == "3":#cantilever
            while True:
                types_bars = get_input("How many bars of different diameter you want to give? : ", int, allow_back=True)
                if types_bars == "BACK":
                    break
                inner_span = get_input("Enter the inner span for cantilever: ", allow_back=True)
                if inner_span == "BACK":
                    continue
                canti_span = get_input("Enter the cantilever span: ", allow_back=True)
                if canti_span == "BACK":
                    continue
                for i in range(types_bars):
                    d = get_input(f"Enter diameter of bar {i+1} (in mm): ", allow_back=True)
                    if d == "BACK":
                        break
                    beam_num = get_input("Enter the beam number of this cantilever: ", int, allow_back=True)
                    if beam_num == "BACK":
                        break
                    length = flow4(inner_span, canti_span)
                    if theLoop(length, results, choice, 0, 0, 0, d, beam_num) == "BACK":
                        break
                break
        
        elif choice == "4":
            stirrup_flow()

        elif choice == "5":
            slab_flow()
            
    # Summary
    print("\nSummary of cutting lengths:\n")
    field_order = ["type", "beam no.", "clear span", "bend length1", "bend length2", "quantity"]
    field_names = ["Beam Type", "Beam No.", "Clear Span", "Bend len 1", "Bend len 2", "quantity"]
    group_by_field(results, group_key="d", field_order=field_order, field_names=field_names, title_prefix="(Diff spacing) Bar dia")

if __name__ == "__main__":
    main()
