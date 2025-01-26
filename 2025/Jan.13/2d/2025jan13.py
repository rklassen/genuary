from PIL import Image, ImageDraw
import math, random

# region pseudo-constants
RESOLUTION    = 1024  # width and height of image
DISPLACEMENT  = 0.094 # scalar in uv space for frond gravity and trunk "lean"
N_FROND       = 64    # number of triangles per frond
COLOR_NOISE   = 8     # added (+/-) to each rgb component
CENTRAL_COLOR = ( 100, 255, 128 )
FROND_TIP     = ( 150,  96, 255 )
TRUNK_BASE    = ( 120,  30, 200 )
TRUNK_TOP     = ( 255, 250, 120 )
INFLO_COLOR   = ( 200, 250, 120 )
BG_SKY        = (  96,   0, 128 )
BG_HORIZON    = ( 255,  64,   0 )
BG_WATER      = ( 255,  90,   8 )
BG_NADIR      = (  96,   0, 128 )
HORIZON       = 0.72
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

# third_vertex is a vertical displacement to create leaflets.
def draw_triangle(center_u, center_v, radius, angle, color, third_vertex: int = 0):
    x1 = center_u + radius * math.cos(angle)
    y1 = center_v + radius * math.sin(angle)
    x2 = center_u + radius * math.cos(angle + 2 * math.pi / 3)
    y2 = center_v + radius * math.sin(angle + 2 * math.pi / 3)
    x3 = center_u + radius * math.cos(angle + 4 * math.pi / 3)
    y3 = center_v + radius * math.sin(angle + 4 * math.pi / 3)
    draw.polygon([(x1 * RESOLUTION, y1 * RESOLUTION), 
                  (x2 * RESOLUTION, y2 * RESOLUTION), 
                  (x3 * RESOLUTION, (y3 + third_vertex) * RESOLUTION)], 
                  fill = color)

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
        u = begin_u + t * (end.uv.u - begin_u) + t * random.uniform(-0.01, 0.01)
        v = begin_v + t * (end.uv.v - begin_v) + t * random.uniform(-0.01, 0.01)
        r = begin_r + t * (end.r - begin_r)
        x = t * t * displacement.v * DISPLACEMENT * RESOLUTION
        y = t * t * displacement.u * DISPLACEMENT * RESOLUTION
        theta = random.uniform(0, 2 * math.pi)
        rgb = [min(255, max(0, int(begin.color[j] + t * (end.color[j] - begin.color[j]) 
                                   + random.uniform(-COLOR_NOISE, COLOR_NOISE)))) 
                                   for j in range(3)]
        leaflet_taper = math.sqrt(1.0 - t)
        s = max(0.0, 0.167 - t) / 0.167
        base_taper = 1.0 - s * s
        third_vertex = leaflet_factor * base_taper * leaflet_taper / 10
        draw_triangle(u + x, v + y, r, theta, tuple(rgb), third_vertex)
# endregion init

# region bg
BG_LINE_COUNT = 36.0
BG_LINE_WIDTH = 1.0 / BG_LINE_COUNT + 0.01
for line_index in range ( int ( BG_LINE_COUNT ) + 1):
    u = float ( line_index ) / BG_LINE_COUNT
    du = abs ( u - 0.4 )
    v = HORIZON + du * du / 9.0
    begin = NodeData ( uv = vec2 ( u, 0 ), r = BG_LINE_WIDTH, color = BG_SKY )
    end   = NodeData ( uv = vec2 ( u, v ), r = BG_LINE_WIDTH, color = BG_HORIZON )
    draw_line ( 100, begin, end, vec2 ( 0.0, 0.0 ) )
    begin = NodeData ( uv = vec2 ( u, v ), r = BG_LINE_WIDTH, color = BG_WATER )
    end   = NodeData ( uv = vec2 ( u, 1.0 ), r = BG_LINE_WIDTH, color = BG_NADIR )
    draw_line ( 100, begin, end, vec2 ( 0.0, 0.0 ) )
# endregion

# region trunk
begin = NodeData ( uv = vec2(0.46, 0.813), r = 0.04, color = TRUNK_BASE )
end   = NodeData ( uv = vec2(0.46, 0.352), r = 0.01, color = TRUNK_TOP )
draw_line ( 140, begin, end, vec2( 0.0, 0.0008 ) )
# endregion trunk

# region inflorescence 
uv_0 = vec2 ( 0.46 + 1.0 * DISPLACEMENT, 0.34 )
uv_1 = vec2 ( 0.46 + 0.8 * DISPLACEMENT, 0.38 )
begin_inflorescence = NodeData ( uv = uv_1, r = 0.06, color = INFLO_COLOR )
end_inflorescence   = NodeData ( uv = uv_0, r = 0.02, color = CENTRAL_COLOR )
draw_line ( N_FROND, begin_inflorescence, end_inflorescence, vec2 ( 0, 0 ) )
# endregion inflorescence

# region fronds
# begin and end coordinates in texture space for each frond
# prior to both displacement and third vertex adjustment
uv_0 = vec2 ( u = 0.46 + DISPLACEMENT, v = 0.412 )
uvs_1 = [
    vec2 ( u = 0.21, v = -0.35 ),  # left 04
    vec2 ( u = 0.29, v = -0.05 ),  # left 03
    vec2 ( u = 0.21, v =  0.05 ),  # left 02
    vec2 ( u = 0.16, v =  0.25 ),  # left 01
    vec2 ( u = 0.29, v =  0.41 ),  # bottom left 00
    vec2 ( u = 0.64, v = -0.15 ),  # right 03
    vec2 ( u = 0.76, v =  0.05 ),  # right 02
    vec2 ( u = 0.76, v =  0.15 ),  # right 01
    vec2 ( u = 0.79, v =  0.30 ),  # bottom right 00
]
frond_displacement = [ float(value) / RESOLUTION for value in [7, 5, 3, 3, 2, 4, 2, 2, 3]]

for frond_index in range ( len ( uvs_1 ) ):
    begin_frond = NodeData ( uv = uv_0,                r = 0.01, color = CENTRAL_COLOR )
    end_frond   = NodeData ( uv = uvs_1 [ frond_index ], r = 0.01, color = FROND_TIP )
    this_displacement = vec2 ( u = frond_displacement [ frond_index ], v = 0.0 )
    draw_line ( N_FROND, begin_frond, end_frond, this_displacement, 1.0 )
# endregion fronds

image.save('2025jan13.png')