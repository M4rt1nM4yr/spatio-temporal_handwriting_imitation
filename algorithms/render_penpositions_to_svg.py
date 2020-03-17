
def ColorGenerator():
    while True:
        yield '#1f77b4'
        yield '#ff7f0e'
        yield '#2ca02c'
        yield '#d62728'
        yield '#9467bd'
        yield '#8c564b'
        yield '#e377c2'
        yield '#7f7f7f'
        yield '#bcbd22'
        yield '#17becf'


def render_penpositions_to_svg(penPositions, svg):

    points = list()

    colors = ColorGenerator()
    color = next(colors)

    for penPosition in penPositions:
        points.append(penPosition.pos)
        svg.add(svg.circle(center=penPosition.pos, r=2, fill=color, stroke='none'))
        if penPosition.penUp > 0.5:
            #print(points)
            svg.add(svg.polyline(points, stroke_width=2, fill='none', stroke=color, stroke_opacity="0.5"))
            points = list()
            color = next(colors)
    if points:
        svg.add(svg.polyline(points, stroke_width=2, fill='none', stroke=color, stroke_opacity="0.5"))

