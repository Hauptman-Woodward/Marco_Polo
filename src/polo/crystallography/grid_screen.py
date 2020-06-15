import math


class Plate():

    UNITS = ['M', '(w/v)', '(v/v)']

    def __init__(self, x_wells, y_wells, x_reagent, y_reagent, constants,
                 x_step, y_step, well_volume):
        self.x_wells = int(x_wells)
        self.y_wells = int(y_wells)
        self.x_step = x_step
        self.y_step = y_step
        self.y_reagent = y_reagent
        self.x_reagent = x_reagent
        self.well_volume = well_volume

    @property
    def number_wells(self):
        return self.x_wells * self.y_wells
    # NOTE:
    # All percentage based units should be converted to proportions
    # first before any operations happen with them 

    # NOTE:
    # Gradients for each axis are calculated by getting the volume of stock
    # solution of that reagent required to replicate the hit concentration
    # at the well volume determined by the plate instance
    # if that cannot be obtained due to lack of chemical formula or a
    # reagent unit that resists conversion to molarity like (v/v)
    # then we subsitute just the reagent concentration and varry that
    # long the given axis. If the case of v / v we assume there is some
    # premade stock that the user will know about to use. Can still do
    # validation with these units though to see if need a higher stock
    # concentration

    @property
    def x_gradient(self):
        stock_volume, units = self.x_reagent.stock_volume(
            self.well_volume), None
        if stock_volume:
            c = stock_volume
            units = 'L'  # molarity b/c was able to convert
        else:
            c = self.x_reagent.concentration  # varry the actual unit as is
            # units are in whatever it was originally
            units = self.x_reagent.concentration_units
        m = math.floor(self.x_wells / 2)
        s = c * self.x_step
        return [c + (s * (n - m)) for n in range(1, self.x_wells)], units

    @property
    def y_gradient(self):
        stock_volume, units = self.y_reagent.stock_volume(
            self.well_volume), None
        if stock_volume:
            c = stock_volume
            units = 'L'  # really should be volume of stock in liters
        else:
            c = self.y_reagent.concentration
            units = self.y_reagent.concentration_units
        m = math.floor(self.y_wells / 2)
        s = c * self.y_step
        return [c + (s * (n - m)) for n in range(1, self.y_wells)], units

    def write_current_grid(self):
        grid = []
        if check_for_fit():
            x_grad, y_grad = self.x_gradient, self.y_gradient
            for i in range(0, self.x_wells):
                grid.append([])
                for j in range(0, self.y_wells):
                    grid[i].append[
                        (x_grad[i], y_grad[j])
                    ]
    # TODO: Need to parse out that stock solution to add the correct
    # units. Will always be of stock units change


    def well_string_formater(self, amount, chem_name):
        return ''  # TODO implement this method so returns
        # standard formated string that would eventually be displayed to
        # the user in a table view type format

    
    def volume_gradient(self, grad, units):
        if units == 'L':  # units in liters
            return grad
        elif units == self.UNITS[1]:
            # could varry by grams needed to add to solution
            pass
        elif units == self.UNITS[2]:
            return [(x*self.well_volume) for x in grad]
    # put units into volume so can calculate if the total
    # volume of the well will be greater than what is contained

    def check_for_fit(self):
        x_grad, x_units = self.x_gradient
        y_grad, y_units - self.y_gradient
        x_vol_grad = self.volume_gradient(x_grad, x_units)
        y_vol_grad = self.volume_gradient(y_grad, y_units)

        for i in range(0, self.x_wells):
            for j in range(0, self.y_wells):
                total_volume = x_vol_grad[i] + y_vol_grad[j]
                if total_volume > self.well_volume:
                    return False  # at least one well will overflow
        return True


