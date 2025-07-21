def bend_length(d, sup_width,beam_depth):
    ld = 46 * d
    switch = sup_width - 20 + beam_depth - 25 
    safe_len = ld - sup_width - 20 - 2 * d
    if ld > switch:
        return max(0, safe_len)
    else:
        return max(0, ld)

def flow1(d, clear_span, es_width1, es_width2, bl1, bl2):
    cutting_len = clear_span + es_width1 + bl1 + es_width2 + bl2
    return cutting_len

def flow2(d, clear_span, es_width, beam_depth, bl1):
    ld_cont = 46 * d
    cutting_len = clear_span + bl1 + ld_cont + es_width
    return cutting_len

def flow3(d, clear_span):
    cutting_len = clear_span + 2 * 46 * d
    return cutting_len

def flow4(inner_span, canti_span): #cantilever 
    return inner_span / 3 + canti_span + 150 
