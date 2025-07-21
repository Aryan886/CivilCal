from cuttingLen import flow1, flow2, flow3, flow4, bend_length
from result import theLoop, group_by_field
from inputs import get_input
from stirrups import stirrup_flow
from slab import slab_flow
from fpdf import FPDF
import os

def menu():
    print("\nCutting Length Calculator for Continuous Bars")
    print("DO NOTE ALL INPUTS/OUTPUTS ARE TO BE IN MM")
    print("1. Top Steel")
    print("2. Bottom Steel")
    print("3. Cantilever Top Steel")
    print("4. Stirrups")
    print("5. Slab")
    print("6. Exit") 

def write_pdf(results, pdf_path, field_order, field_names, group_key, title_prefix=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Cutting Length Calculator Results', ln=True, align='C')
    pdf.ln(5)
    from collections import defaultdict
    grouped = defaultdict(list)
    for entry in results:
        grouped[entry[group_key]].append(entry)
    pdf.set_font('Arial', '', 12)
    for key_val, entries in grouped.items():
        title = f"{title_prefix or group_key.title()}: {key_val}"
        pdf.cell(0, 10, title, ln=True)
        headers = field_names if field_names else [k.replace('_', ' ').title() for k in field_order]
        col_widths = [30] * len(headers)
        pdf.set_font('Arial', 'B', 12)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, str(h), border=1)
        pdf.ln()
        pdf.set_font('Arial', '', 12)
        for e in entries:
            for i, key in enumerate(field_order):
                val = e.get(key, "")
                if isinstance(val, float):
                    val = f"{val:.2f}"
                pdf.cell(col_widths[i], 8, str(val), border=1)
            pdf.ln()
        pdf.ln(2)
    pdf.output(pdf_path)

def main():
    results = []
    pdf_path = None
    try:
        while True:
            if pdf_path is None:
                pdf_name = input("Enter the name for the PDF file (without extension): ").strip()
                if not pdf_name:
                    pdf_name = "cutting_length_results"
                # Ensure the pdfs directory exists
                os.makedirs("pdfs", exist_ok=True)
                pdf_path = os.path.join("pdfs", pdf_name + ".pdf")
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
            menu()
            choice = input("Press 1/2/3 as per requirement: ").strip()
            if choice not in ("1", "2", "3", "4", "5"):
                print("\nThank you for using the software.")
                break

            clear_span = beam_num = beam_depth = 0

            if choice in ("1", "2"):#Top and Bottom beam
                while True:
                    beam_num = input("Enter the beam number: ")
                    conti_bar = input("Is this bar extended into other beams?(y/n): ").strip().lower()
                    if conti_bar == "y":
                        clear_span = get_input("Enter the clear span of bar(end-to-end): ", int)
                        es_width1 = get_input("Enter the end support width of first beam (mm): ", int)
                        es_width2 = get_input("Enter the end supp width of second beam (mm): ", int)
                        #beam_depth1 = get_input("Enter beam depth of first supp(mm): ", int)
                        #beam_depth2 = get_input("Enter beam depth of second supp(mm): ", int)
                        types_bars = get_input("Enter number of bar diameters you want to input: ", int, allow_back=True)
                        for i in range(types_bars):
                            d = get_input(f"Enter the diameter of bar {i+1} (mm) : ")
                            bl1 = bend_length(d, es_width1)
                            bl2 = bend_length(d, es_width2)
                            length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                            theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num)
                        break
                    else:
                        end_supp = input("Is the end support present?(y/n): ").strip().lower()
                        if end_supp == "y":
                            quant_end_supp = input("Enter how many end support are present: ").strip().lower()
                            if  quant_end_supp == 1:
                                es_width = get_input("Enter the width of the end support(mm): ")
                                types_bars = get_input("Enter the no. of bars diameters you want to input: ")
                                for i in range(types_bars):
                                    d = get_input(f"Enter diameter of bar{i+1}(mm): ")
                                    bl1 = bend_length(d, es_width)
                                    bl2 = 0
                                    length = flow2(d, clear_span, es_width, beam_depth, bl1)
                                    theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num)
                                break

                            elif quant_end_supp == 2:
                                es_width1 = get_input("Enter the width of end support 1(mm): ")
                                es_width2 = get_input("Enter the width of end support 2(mm): ")
                                types_bars = get_input("Enter the number of bar diameters you want to input(mm): ")
                                for i in range(types_bars):
                                    d = get_input(f"Enter the diameter of bar {i+1}(mm): ")
                                    bl1 = bend_length(d, es_width1)
                                    bl2 = bend_length(d, es_width2)
                                    length = flow1(d, clear_span, es_width1, es_width2, beam_depth, bl1, bl2)
                                    theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num)
                                break
                            
                            else:
                                print("Enter either 1 or 2")
                                break
                        
                        else:
                            types_bars = get_input("Enter number of bar diameters you want to input: ", int, allow_back=True)
                            for i in range(types_bars):
                                d = get_input(f"Enter the diameter of bar {i+1} (mm) : ")
                                bl1 = bend_length(d, es_width1)
                                bl2 = bend_length(d, es_width2)
                                length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                                theLoop(length, results, choice, clear_span, bl1, bl2, d, beam_num)
                            break


            elif choice == "3":#cantilever
                while True:
                    conti_bar = input("Does it extend upto dead-end(y/n): ").strip().lower()
                    if conti_bar == "y":
                        clear_span = get_input("Enter the full span(mm):  ")
                        types_bars = get_input("How many bars of different diameter you want to give? : ", int, allow_back=True)
                        for i in range(types_bars):   
                            d = get_input(f"Enter diameter of bar {i+1} (in mm): ", allow_back=True)
                            beam_num = get_input("Enter the beam number for this cantilever: ")
                            length = clear_span
                            theLoop(length, results, choice, 0, 0, 0, d, beam_num)
                        break
                    else:
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
                            beam_num = get_input("Enter the beam number of this cantilever: ")
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
                
            # After each result is added, update the PDF
            field_order = ["type", "beam no.",  "bend length1", "bend length2", "quantity", "length per bar"]
            field_names = ["Beam Type", "Beam No.","Bend len 1", "Bend len 2", "quantity", "Cutting-length"]
            write_pdf(results, pdf_path, field_order, field_names, group_key="d", title_prefix="(Diff spacing) Bar dia")

        # Summary
        print("\nSummary of cutting lengths:\n")
        field_order = ["type", "beam no.", "bend length1", "bend length2", "quantity", "length per bar"]
        field_names = ["Beam Type", "Beam No.", "Bend len 1", "Bend len 2", "quantity", "Cutting-length"]
        group_by_field(results, group_key="d", field_order=field_order, field_names=field_names, title_prefix="(Diff spacing) Bar dia")

    except KeyboardInterrupt:
        print("\n\nCtrl+C detected. Saving current progress and exiting...")
        if results and pdf_path:
            field_order = ["type", "beam no.",  "bend length1", "bend length2", "quantity", "length per bar"]
            field_names = ["Beam Type", "Beam No.","Bend len 1", "Bend len 2", "quantity", "Cutting-length"]
            group_by_field(results, group_key="d", field_order=field_order, field_names=field_names, title_prefix="(Diff spacing) Bar dia")
            write_pdf(results, pdf_path, field_order, field_names, group_key="d", title_prefix="(Diff spacing) Bar dia")
            print(f"Results saved to {pdf_path}")
        print("Thank you for using the software.")

if __name__ == "__main__":
    main()
