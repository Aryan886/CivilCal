from inputs import get_input
from result import group_by_field, show_custom_results
import math

def different_spacing(l4_spacing, clear_span, l2_spacing, weight_bar, stirrups_data,type_stirrup,d,beam_num,cutting_len):
    # this for l/4 spacing
    y = l4_spacing
    x = clear_span/4
    num_stirrups1 = math.floor((x/y) + 1)
    tweigth1 = weight_bar*num_stirrups1*2
    #this for l/2 spacing 
    w = l2_spacing
    z = clear_span/2
    num_stirrups2 = math.floor((z/w) + 1)
    tweigth2 = weight_bar*num_stirrups2
    total_weight = tweigth2 + tweigth1
    stirrups_data.append({
        "type": "Two legged" if type_stirrup == "1" else "4 legged" if type_stirrup == "2"  else "6 legged",
        "beam_num": beam_num,
        "d": d,
        "num_l/4_stirrups" : num_stirrups1,
        "num_l/2_stirrups" : num_stirrups2,
        "cutting_len": cutting_len,
        "total_weight": math.floor(total_weight/1000),
        "spacing type": "diff"
    })
    

def same_spacing(clear_span,spacing,weight_bar,stirrups_data,type_stirrup, beam_num, cutting_len,d):
    num_stirrups = math.floor(clear_span/spacing)
    total_weight = num_stirrups*weight_bar
    stirrups_data.append({
        "type": "Two legged" if type_stirrup == "1" else "4 legged" if type_stirrup == "2"  else "6 legged",
        "beam_num": beam_num,
        "d": d,
        "num_stirrups": num_stirrups,
        "cutting_len": cutting_len,
        "total_weight": math.floor(total_weight/1000),
        "spacing type": "uniform"
    })


def menu():
    print("1. Two legged")
    print("2. four legged")
    print("3. six legged")
    print("4. Exit")

def stirrup_flow():
    stirrups_data = []

    while True:
        menu()
        type_stirrup = input("Enter 1/2/3 as per req : ").strip()
        if type_stirrup == "4":
            break

        clear_span = get_input(prompt="Enter the clear span : ")
        beam_width = get_input(prompt="Enter beam width : ")
        beam_depth = get_input(prompt="Enter beam depth : ")
        beam_num = get_input(prompt="Enter beam no. ")
        d = get_input(prompt="Enter the diameter of bar : ")

        if type_stirrup == "1":
            choice = input("Is spacing diff? (y/n) : ")
            a = beam_width - 40
            b = beam_depth - 40
            cutting_len = 2*a + 2*b + 20*d - 6*d - 6*d
            weight_bar = ((d*d)/162)*cutting_len

            if choice == "y":#spacing is diff
                l4_spacing = get_input(prompt="Enter spacing for L/4 : ")
                l2_spacing = get_input(prompt="Enter spacing for remaining : ")
                different_spacing(l4_spacing, clear_span, l2_spacing, weight_bar, stirrups_data,type_stirrup,d,beam_num,cutting_len)

            else:
                spacing = get_input(prompt="Enter the spacing : ")
                same_spacing(clear_span,spacing,weight_bar,stirrups_data,type_stirrup, beam_num, cutting_len,d)
        
        elif type_stirrup == "2":
            choice = input("Is spacing diff? (y/n) : ")
            a = beam_depth - 40
            b =  beam_width - 40
            cutting_len = math.floor(4*a + 2*b +2*(b/3) +16*d)
            weight_bar = math.floor((d*d/162)*cutting_len)

            #Repeating code block [try to make it into reusable func later]
            if choice == "y":#spacing is diff
                l4_spacing = get_input(prompt="Enter spacing for L/4 : ")
                l2_spacing = get_input(prompt="Enter spacing for remaining : ")
                different_spacing(l4_spacing, clear_span, l2_spacing, weight_bar, stirrups_data,type_stirrup,d,beam_num,cutting_len)
            else:
                spacing = get_input(prompt="Enter the spacing : ")
                same_spacing(clear_span,spacing,weight_bar,stirrups_data,type_stirrup, beam_num, cutting_len,d)
        
        elif type_stirrup == "3":
            choice = input("Is spacing different (y/n) : ")
            a = beam_depth - 40
            b = beam_width - 40
            cutting_len = math.floor(6*a + 2*b + 4*b/5 + 24*d)
            weight_bar = math.floor((d*d/162)*cutting_len)
            if choice == "y":#spacing is diff
                l4_spacing = get_input(prompt="Enter spacing for L/4 : ")
                l2_spacing = get_input(prompt="Enter spacing for remaining : ")
                different_spacing(l4_spacing, clear_span, l2_spacing, weight_bar, stirrups_data,type_stirrup,d,beam_num,cutting_len)
            else:
                spacing = get_input(prompt="Enter the spacing : ")
                same_spacing(clear_span,spacing,weight_bar,stirrups_data,type_stirrup, beam_num, cutting_len,d)

    #Summary
    diff_spacing = [x for x in stirrups_data if x["spacing type"] == "diff"]
    uniform_spacing = [x for x in stirrups_data if x["spacing type"] == "uniform"]

    if diff_spacing:
        field_order = ["type","beam_num", "num_l/4_stirrups", "num_l/2_stirrups", "cutting_len", "total_weight"]
        field_names = ["Beam Type","Beam no.", "No. of L/4 stirrups", "No. of L/2 stirrups", "Cutting Len (mm)", "Total Weight (kg)"]
        group_by_field(diff_spacing, group_key="d", field_order=field_order, field_names=field_names, title_prefix="(Diff spacing) Bar dia")

    if uniform_spacing:
        field_order = ["type","beam_num", "num_stirrups", "cutting_len", "total_weight"]
        field_names = ["Beam Type","Beam no.", "No. of stirrups", "Cutting Len", "Total Weight (kg)"]
        group_by_field(uniform_spacing, group_key="d", field_order=field_order, field_names=field_names, title_prefix="(Uniform spacing) Bar dia")


if __name__ == "__main__":
    stirrup_flow()