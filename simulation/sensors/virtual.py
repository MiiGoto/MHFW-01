def product_sensor(products,x,length):
    return any(abs(p['x']-x)<=length/2 for p in products)
def in_seal_zone(products,x,length):
    return any(abs(p['x']-x)<length/2+5 for p in products)
