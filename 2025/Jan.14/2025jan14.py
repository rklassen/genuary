from PIL import Image, ImageDraw
import math, random

# region pseudo-constants
RESOLUTION = 1024   # width and heigh of image
DISPLACEMENT = 96   # number of pixels 
N_FROND = 64        # number of triangles per frond
# endregion

# region pseudo-structs
class NodeData:
    def __init__(self, uv, r, color):
        self.uv = uv
        self.r = r
        self.color = color

class vec2:
    def __init__(self, u, v):
        self.u = u
        self.v = v
# endregion pseudostructs

# region init
image = Image.new("RGB", (RESOLUTION, RESOLUTION), "black")
draw = ImageDraw.Draw(image)

# third_vertex is a vertical displacement to to create leaflets.
def draw_triangle(center_u, center_v, radius, angle, color, third_vertex: int = 0):
    x1 = center_u + radius * math.cos(angle)
    y1 = center_v + radius * math.sin(angle)
    x2 = center_u + radius * math.cos(angle + 2 * math.pi / 3)
    y2 = center_v + radius * math.sin(angle + 2 * math.pi / 3)
    x3 = center_u + radius * math.cos(angle + 4 * math.pi / 3)
    y3 = center_v + radius * math.sin(angle + 4 * math.pi / 3)
    c0 = color, color, color
    draw.polygon([(x1, y1), (x2, y2), (x3, y3+third_vertex)], outline=c0, width=1)

# leaflet_factor argument = [0.0 for trunk, 1.0 for fronds].
def draw_line(n: int, 
               begin: NodeData, 
               end: NodeData, 
               displacement: vec2, 
               leaflet_factor: float = 0.0):
    
    # scale the fronds from center of array to avoid overlaps with inflorescence
    begin_u = begin.uv.u + leaflet_factor * 0.167 * (end.uv.u - begin.uv.u)
    begin_v = begin.uv.v + leaflet_factor * 0.167 * (end.uv.v - begin.uv.v)
    begin_r = begin.r    + leaflet_factor * 0.167 * (end.r - begin.r)
    for index in range(n):
        t = float(index)/float(n)
        u = begin_u + t * (end.uv.u - begin_u) + t * random.uniform(-10.0, 10.0)
        v = begin_v + t * (end.uv.v - begin_v) + t * random.uniform(-10.0, 10.0)
        r = begin_r + t * (end.r - begin_r)
        x = t * t * displacement.v * DISPLACEMENT
        y = t * t * displacement.u * DISPLACEMENT
        theta = random.uniform(0, 2 * math.pi)
        rgb = int(begin.color + t * float(end.color - begin.color))
        rgb += random.randint(0, 32)
        leaflet_taper = math.sqrt(1.0 - t)
        s = max(0.0, 0.167 - t) / 0.167
        base_taper = 1.0 - s * s
        third_vertex = leaflet_factor * base_taper * leaflet_taper * RESOLUTION / 10
        draw_triangle(u + x, v + y, r, theta, rgb, third_vertex)
# endregion init

# region trunk
begin_uv = vec2 ( -42 + RESOLUTION / 2.20, 53 + 0.80 * RESOLUTION )
end_uv   = vec2 ( -42 + RESOLUTION / 2.10, 53 + 0.32 * RESOLUTION )
begin = NodeData ( uv = begin_uv, r = 40, color =  64 )
end   = NodeData ( uv = end_uv, r = 10, color = 128 )
draw_line ( 200, begin, end, vec2( 0.0, 1.1 ) )
# endregion trunk

# region frond
# begin and end coordinates in texture space for each frond
# prior to both displacement and third vertex adjustment
begin_uv = vec2 ( u = -42 + RESOLUTION / 2.0 + DISPLACEMENT, v = 53 + 0.36 * RESOLUTION )
end_uvs = [
    vec2 ( u = -42 + RESOLUTION / 3,     v = 53 + 0.36 * RESOLUTION ),  # bottom left 00
    vec2 ( u = -42 + RESOLUTION / 5,     v = 53 +  0.2 * RESOLUTION ),  # left 01
    vec2 ( u = -42 + RESOLUTION / 4,     v = 53 +    0 * RESOLUTION ),  # left 02
    vec2 ( u = -42 + RESOLUTION / 3,     v = 53 + -0.1 * RESOLUTION ),  # left 03
    vec2 ( u = -42 + RESOLUTION / 2.25,  v = 53 + -0.4 * RESOLUTION ),  # left 04
    vec2 ( u = -42 + RESOLUTION * 5 / 6, v = 53 + 0.25 * RESOLUTION ),  # bottom right 00
    vec2 ( u = -42 + RESOLUTION * 4 / 5, v = 53 +  0.1 * RESOLUTION ),  # right 01
    vec2 ( u = -42 + RESOLUTION * 4 / 5, v = 53 +  0.0 * RESOLUTION ),  # right 02
    vec2 ( u = -42 + RESOLUTION * 2 / 3, v = 53 + -0.2 * RESOLUTION ),  # right 03
]
frond_displacement = [ 2.0, 3.0, 3.0, 5.0, 7.0, 3.0, 2.0, 2.0, 4.0 ]

for frond_index in range ( len ( end_uvs ) ):
    begin_frond = NodeData ( uv = begin_uv,                r = 10, color = 128 )
    end_frond   = NodeData ( uv = end_uvs [ frond_index ], r = 10, color =  96 )
    this_displacement = vec2 ( u = frond_displacement [ frond_index ], v = 0.0 )
    draw_line ( N_FROND, begin_frond, end_frond, this_displacement, 1.0 )
# endregion fronds

# region inflorescence 
infl_uv_0 = vec2 ( u = -42 + 0.50 * RESOLUTION + DISPLACEMENT / 2, 
                   v =  53 + 0.33 * RESOLUTION )
infl_uv_1 = vec2 ( u = -42 + 0.50 * RESOLUTION + DISPLACEMENT,
                   v =  53 + 0.29 * RESOLUTION )
begin_inflorescence = NodeData ( uv = infl_uv_0, r = 24, color = 128 )
end_inflorescence   = NodeData ( uv = infl_uv_1, r = 48, color = 256 )
draw_line ( N_FROND, begin_inflorescence, end_inflorescence, vec2 ( 0, 0 ) )
# endregion inflorescence

image.save('2025jan14.png')