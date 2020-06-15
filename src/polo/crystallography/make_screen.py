def make_tray(total_volume, hit_concentration, total_wells,
              sample_concentration, sample_volume_per_well,
              stock_cocentration, step_percent):
    pass


def get_dilution(target_con, stock_con):
    # assume both are in M
    pass

def get_stock_volume(target_con, total_volume, stock_con):
    return (target_con * total_volume) / stock_con



def get_mols(total_volume, target_con):
    return target_con * total_volume  # target_con M/L V = Liters


    


def get_usable_volume(total_volume):
    pass

def calculate_row(volume, x_con, x_stock_con, y_stock_con, y_con, y_step, steps):
    base = round(steps / 2)
    increment = y_con * y_step  # y_step between 1 and 0
    min_con = y_con - (base * increment)
    y_cons = [min_con + (increment*i) for i in range(steps)]
    
    
    # y cons should be in M
    print(y_cons)
    y_cons = [get_stock_volume(y_con, volume, y_stock_con)for y_con in y_cons]
    # do this in a loop for when more than one constant