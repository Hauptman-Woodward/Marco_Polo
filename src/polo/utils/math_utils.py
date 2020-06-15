import math

def factors(n):
    facts = []
    for i in range(1, int(pow(n, 1 / 2))+1): 
        if n % i == 0:
            facts.append((int(n / i), i))
    return facts

def best_aspect_ratio(w, h, n):
    a = w / h
    potentail_aspects = factors(n)
    aspect_diffs = [abs((w / h) - a) for w, h in potentail_aspects]
    min_diff_index = aspect_diffs.index(min(aspect_diffs))
    return potentail_aspects[min_diff_index]

def get_image_cell_size(cell_aspect, w, h):
    x, y = cell_aspect  # aspect ratio width and height ints 
    max_w, max_h = w / x, h / y  # w and h in pixels apsect ratio unitless
    return math.floor(min(max_h, max_w))  # largest square image size


def get_cell_image_dims(w, h, n):
    a = best_aspect_ratio(w, h, n)
    q = get_image_cell_size(a, w, h)
    return (q, q)  # always a square