from typing import List

from qiskit_metal import draw, Dict,designs
from qiskit_metal.qlibrary.core import BaseQubit
from qiskit_metal.toolbox_metal import math_and_overrides
from qiskit_metal.qlibrary.core import QComponent
from qiskit_metal.draw import LineString
from qiskit_metal import MetalGUI, Dict, Headings
from qiskit_metal.qlibrary.core.qroute import QRouteLead, QRoutePoint, QRoute
from qiskit_metal.qlibrary.qubits.transmon_cross import TransmonCross
from qiskit_metal.qlibrary.resonator.readoutres_fc import ReadoutResFC
from  qiskit_metal.qlibrary.user_components.my_qcomponent import  New_Transmon_Cross, RouteConnector,MyReadoutRes01,MyReadoutRes02,MyFluxLine01,MyFluxLine02,MyConnector,MyXYLine01,MyCircle
from  qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder
from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond
import  math
from collections import  OrderedDict
import numpy as np
import time
from tqdm import  tqdm, trange



design = designs.DesignPlanar()
# Specify design name
design.metadata['design_name'] = 'FlipChip_Device'
# launch GUI
gui = MetalGUI(design)
# Allow running the same cell here multiple times to overwrite changes
design.overwrite_enabled = True


design.chips['main']['material'] = 'sapphire'
design.chips['main']['size']['size_x'] = '15.14 mm'
design.chips['main']['size']['size_y'] = '26 mm'
design.variables.cpw_gap='5 um'
# design.chips,design.variables
my_chip = MyCircle(design,'my_chip', options=Dict(radius='35mm'))

# design the layout of launchpad
points = []
N=42
size = 32.0
pad_pad_space = 0.7
edge_gap = (size -(pad_pad_space*(N-1)))/2
for i in range(N):
    shape = draw.Point(-size/2+edge_gap+i*pad_pad_space,size/2)
    points.append(shape)
# points.append()
# for i in range(N):
#     shape = draw.Point(size/2,size/2-i*size/N)
x = draw.shapely.geometrycollections(points)
x0 = draw.rotate(x,90,origin=(0,0))
x1 = draw.rotate(x0,90,origin=(0,0))
x2 = draw.rotate(x1,90,origin=(0,0))
square = draw.shapely.geometrycollections([x,x0,x1,x2])
square = draw.rotate(square,45,origin=(0,0))
square_coords =[]
for i in range(4):
    for j in range(N):
        square_coords.append(square.geoms[i].geoms[j].coords[0])

opt=Dict(pos_x=0 , pos_y=0, orientation='-45', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'main')
opt_a=Dict(pos_x=0 , pos_y=0, orientation='45', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'main')
opt_b=Dict(pos_x=0 , pos_y=0, orientation='135', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'main')
opt_c=Dict(pos_x=0 , pos_y=0, orientation='-135', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'main')
# test = OpenToGround(design, 'open01', options=Dict(pos_x='-3 mm',  pos_y=pos_y_zline+0.02, orientation='-45', chip ='C_chip'),)
launch_zline = LaunchpadWirebond(design,'launch_zline',options=opt)
launch_zline_a = LaunchpadWirebond(design,'launch_zline_a',options=opt_a)
launch_zline_b = LaunchpadWirebond(design,'launch_zline_b',options=opt_b)
launch_zline_c = LaunchpadWirebond(design,'launch_zline_c',options=opt_c)

design.delete_all_components()
launch_list = []
for i in range(4):
    for j in range(N):
         if (i==0):
            launch_list.append(design.copy_qcomponent(launch_zline,'launch_zline'+str(i)+str(j), Dict(pos_x =square_coords[i*N+j][0] ,pos_y=square_coords[i*N+j][1])))
         elif (i==1):
             launch_list.append(design.copy_qcomponent(launch_zline_a,'launch_zline'+str(i)+str(j), Dict(pos_x =square_coords[i*N+j][0] ,pos_y=square_coords[i*N+j][1])))
         elif (i==2):
             launch_list.append(design.copy_qcomponent(launch_zline_b,'launch_zline'+str(i)+str(j), Dict(pos_x =square_coords[i*N+j][0] ,pos_y=square_coords[i*N+j][1])))
         else:
             launch_list.append(design.copy_qcomponent(launch_zline_c,'launch_zline'+str(i)+str(j), Dict(pos_x =square_coords[i*N+j][0] ,pos_y=square_coords[i*N+j][1])))

# draw an Xmon on the Q_chip. Notice that I have defined one more item called chip and set it to be the 'Q_chip'
# position the center of the Xmon at (0,0)
q0_x = 0
q0_y = 0

# build the device, positioned at (q1_x, q1_y)
# q1 = TransmonCross(design, 'Q1', options = Dict(pos_x=q1_x, pos_y=q1_y, **options))
q0 = New_Transmon_Cross(design, 'Q0', options = Dict(pos_x=q0_x, pos_y=q0_y, cross_inside_width='25um',layer='2'))
q0.options.gds_cell_name = 'FakeJunction_01'

#design the 100 qubits layout
qq_space = 0.015
qubit_num = 18
total_qubit_num = 101
qubit_num0= qubit_num+5
qubit_pos_list = []
y1 = q0.parse_options().cross_width+qq_space
y2 = -1*(q0.parse_options().cross_width+qq_space)
x1 = -int((qubit_num)/4)*y1          #divide qubits into four parts for location calculation

q0.options.pos_y = -y1
q0_y =q0.options.pos_y


for i in range(int(qubit_num)):
    if  (i<(qubit_num)/2):
        qubit_pos_list.append((q0_x+x1+i*y1,q0_y+y1))
    else:
        qubit_pos_list.append((q0_x+x1+(i-qubit_num/2)*y1,q0_y+y2))

q0.options.pos_y = -y1
q0_y =q0.options.pos_y

qubit_list = []
qubit_list.append(q0)
for i in range(int(qubit_num)):
     qubit_list.append(design.copy_qcomponent(q0,'Q'+str(i+1), Dict(pos_x =qubit_pos_list[i][0] ,pos_y=qubit_pos_list[i][1])))

qubit_list.append(design.copy_qcomponent(q0,'Q19', Dict(pos_x =q0_x+x1 ,pos_y=q0_y)))
qubit_list.append(design.copy_qcomponent(q0,'Q20', Dict(pos_x =-(q0_x+x1) ,pos_y=q0_y)))
qubit_list.append(design.copy_qcomponent(q0,'Q21', Dict(pos_x =q0_x+x1/2 ,pos_y=-2*y1+q0_y)))
qubit_list.append(design.copy_qcomponent(q0,'Q22', Dict(pos_x =-x1/2+q0_x ,pos_y=-2*y1+q0_y)))

#draw first part of 100 qubits
qubit_name = []
for i in range(int(qubit_num0)):
    qubit_name.append('Q'+str(i+qubit_num0))
qubit_pos_dict_list =[]
for i in range(int(qubit_num0)):
    qubit_pos_dict_list.append(dict(pos_y = design.components['Q'+str(i)].parse_options().pos_y+4*y1))
qubits_copy1 = design.copy_multiple_qcomponents(qubit_list,qubit_name,qubit_pos_dict_list)

#draw second part
for i in range(int(qubit_num0)):
    qubit_name.append('Q'+str(i+2*qubit_num0))
# qubit_pos_dict_list =[]
for i in range(int(qubit_num0)):
    qubit_pos_dict_list.append(dict(pos_y = design.components['Q'+str(i)].parse_options().pos_y+8*y1))
qubits_copy1 = design.copy_multiple_qcomponents(qubit_list,qubit_name[23:],qubit_pos_dict_list[23:])

#draw third part
for i in range(int(qubit_num0)):
    qubit_name.append('Q'+str(i+3*qubit_num0))
# qubit_pos_dict_list =[]
for i in range(int(qubit_num0)):
    qubit_pos_dict_list.append(dict(pos_y = design.components['Q'+str(i)].parse_options().pos_y-4*y1))
qubits_copy1 = design.copy_multiple_qcomponents(qubit_list,qubit_name[46:],qubit_pos_dict_list[46:])

#draw last part
for i in range(int(qubit_num/2)):
    qubit_name.append('Q'+str(i+4*qubit_num0))
# qubit_pos_dict_list =[]
for i in range(int(qubit_num/2)):
    qubit_pos_dict_list.append(dict(pos_y = design.components['Q'+str(i+1)].parse_options().pos_y-8*y1))
qubits_copy1 = design.copy_multiple_qcomponents(qubit_list[1:int(qubit_num/2+1)],qubit_name[69:],qubit_pos_dict_list[69:])
my_chip = MyCircle(design,'my_chip', options=Dict(radius='35mm'))

# # add the readout resonators
# options = Dict(
#        readout_coupling_width='80 um',
#        readout_coupling_height = '150 um',
#        readout_cpw_width='10 um',
#        readout_cpw_gap='5 um',
#        readout_cpw_turnradius='27 um',
#        vertical_start_length = '40 um',
#        vertical_end_length = '300 um',
#        horizontal_start_length01= '400 um',
#        horizontal_start_length02 = '400 um',
#        horizontal_end_length = '500 um',
#        total_length = '4200 um',
#        arc_step='1 um',
#        meander_round = '5',
#        orientation='0',
#        layer='1',
#        layer_subtract='1',
#        horizontal_end_direction = 'right',
#        inverse = False,
#        mirror = False,
#        subtract=True,
#        chip='main',)
options = Dict(readout_coupling_width='80 um',
                           readout_coupling_height = '100 um',
                           readout_cpw_width='10 um',
                           readout_cpw_gap='5 um',
                           readout_cpw_turnradius='27 um',
                           vertical_start_length = '40 um',
                           vertical_end_length = '300 um',
                           horizontal_start_length01= '400 um',
                           horizontal_start_length02 = '400 um',
                           horizontal_end_length = '500 um',
                           total_length = '3200 um',
                           arc_step='1 um',
                           meander_round = '5',
                           orientation='0',
                           fillet = '5 um',
                           layer='1',
                           layer_subtract='1',
                           horizontal_end_direction = 'right',
                           inverse = False,
                           mirror = False,
                           subtract=True,
                           chip='main',
                           )


location_x = design.components['Q0'].parse_options().cross_width/4
# the resonator is set to have its origin at the center of the circular patch.
# So we set the qubit and the resonator to share the same coordinate (q1_x, q1_y)
r0 = MyReadoutRes02(design, 'R0', options = Dict(pos_x = design.components['Q0'].parse_options().pos_x+location_x, pos_y = design.components['Q0'].parse_options().pos_y, **options))


resonator_list = []
resonator_list.append(r0)
for i in range(int(total_qubit_num)-1):
     location = design.components['Q'+str(i+1)] .parse_options().cross_width/4
     resonator_list.append(design.copy_qcomponent(r0,'R'+str(i+1), Dict(pos_x =design.components['Q'+str(i+1)].parse_options().pos_x+location,pos_y=design.components['Q'+str(i+1)].parse_options().pos_y)))

rr_space = 0.025
design.components['R0'].options.mirror = True
design.components['R0'].options.inverse = True
design.components['R0'].options.meander_round = '3'

# r_0 = design.components['R0'].parse_options().readout_radius
r_0 = design.components['R0'].parse_options().readout_coupling_height/2
r = design.components['R0'].parse_options().readout_cpw_turnradius
l_2 = design.components['R0'].parse_options().vertical_start_length
l_6 = design.components['R0'].parse_options().vertical_end_length
turn_round_n = design.components['R0'].parse_options().meander_round
# vertical_length = r_0+ l_2+2*r*(turn_round_n+1)+l_6

l_v = design.components['R5'].pins.readout.middle[1]-2*rr_space-design.components['R0'].parse_options().pos_y-r_0-l_2-2*r*(turn_round_n+2.5)
design.components['R0'].options.vertical_end_length = l_v

flip_resonator_list = np.array([0,19,20,21,22])
for i in range(3):
    flip_resonator_list = np.concatenate([flip_resonator_list,flip_resonator_list+23])
for i in range(9):
    flip_resonator_list = np.append(flip_resonator_list,92+i)
for i in flip_resonator_list:
    design.components['R'+str(i)].options.mirror = True
    design.components['R'+str(i)].options.inverse = True
    design.components['R'+str(i)].options.meander_round = '3'
    design.components['R'+str(i)].options.vertical_end_length = l_v


for i in [1,24,47,70]:
        design.components['R'+str(i)].options.mirror = True
        design.components['R'+str(i)].options.pos_x =design.components['Q'+str(i)].parse_options().pos_x-location_x
        design.components['R'+str(i+1)].options.mirror = True
        design.components['R'+str(i+1)].options.pos_x =design.components['Q'+str(i+1)].parse_options().pos_x-location_x
        design.components['R'+str(i+1)].options.horizontal_end_direction = 'left'

        design.components['R'+str(i+4)].options.mirror = True
        design.components['R'+str(i+4)].options.pos_x =design.components['Q'+str(i+4)].parse_options().pos_x-location_x
        design.components['R'+str(i+5)].options.mirror = True
        design.components['R'+str(i+5)].options.pos_x =design.components['Q'+str(i+5)].parse_options().pos_x-location_x
        design.components['R'+str(i+5)].options.horizontal_end_direction = 'left'

        design.components['R'+str(i+8)].options.mirror = True
        design.components['R'+str(i+8)].options.pos_x =design.components['Q'+str(i+8)].parse_options().pos_x-location_x

        #---------------------------------------------------------------------------------------------

        design.components['R'+str(i+11)].options.mirror = True
        design.components['R'+str(i+11)].options.pos_x =design.components['Q'+str(i+11)].parse_options().pos_x-location_x
        design.components['R'+str(i+12)].options.mirror = True
        design.components['R'+str(i+12)].options.pos_x =design.components['Q'+str(i+12)].parse_options().pos_x-location_x
        design.components['R'+str(i+12)].options.horizontal_end_direction = 'left'

        design.components['R'+str(i+15)].options.mirror = True
        design.components['R'+str(i+15)].options.pos_x =design.components['Q'+str(i+15)].parse_options().pos_x-location_x
        design.components['R'+str(i+16)].options.mirror = True
        design.components['R'+str(i+16)].options.pos_x =design.components['Q'+str(i+16)].parse_options().pos_x-location_x
        design.components['R'+str(i+16)].options.horizontal_end_direction = 'left'

for i in [22,45,68,91]:
        design.components['R'+str(i)].options.mirror = False
        design.components['R'+str(i)].options.pos_x =design.components['Q'+str(i)].parse_options().pos_x-location_x
        design.components['R'+str(i-6)].options.mirror = False
        design.components['R'+str(i-6)].options.pos_x =design.components['Q'+str(i-6)].parse_options().pos_x+location_x

gui.rebuild()
gui.autoscale()

#set intermediate pins (close to qubits) for layout convenience
unit_y = design.components['Q0'].parse_options().cross_width+qq_space
pin_qubit_list=[]
pin_qubit_num0 = 9
pin_edge_space = 0.3   #horizontal left space for ease
pin_start_space = 0.15   #vertical left space for ease
pin_end_space = 0.25
pos_start_x = design.components['Q65'].parse_options().pos_x-design.components['Q65'].parse_options().cross_width/2-pin_edge_space
pos_start_x_r = design.components['Q66'].parse_options().pos_x+design.components['Q66'].parse_options().cross_width/2+pin_edge_space
# pos_start_y = design.components['Q65'].parse_options().pos_y-pin_start_space
pos_end_x = pos_start_x
# pos_end_y = design.components['Q56'].parse_options().pos_y+pin_end_space
# pin_pin_length = abs(pos_start_y-pos_end_y)
# pin_pin_space = pin_pin_length/(pin_qubit_num0-1)

def set_side_pins(pos_start_x, pin_qubit_num, top_qubit_id, low_qubit_id):
    pos_start_y = design.components['Q'+str(top_qubit_id)].parse_options().pos_y-pin_start_space
    pos_end_y = design.components['Q'+str(low_qubit_id)].parse_options().pos_y+pin_end_space
    pin_pin_space = abs(pos_start_y-pos_end_y)/(pin_qubit_num-1)
    for i in range(pin_qubit_num):
        otg = ShortToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_'+str(i),
                options=Dict(pos_x=pos_start_x,  pos_y=pos_start_y-i*pin_pin_space, orientation='0'))
        otg1 = ShortToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_rhs'+str(i),
        options=Dict(pos_x=pos_start_x,  pos_y=pos_start_y-i*pin_pin_space, orientation='180'))
        pin_qubit_list.append(otg)
        pin_qubit_list.append(otg1)
    return pos_start_y,pos_end_y,pin_pin_space

def set_enlarged_side_pins(pos_start_y, pin_qubit_num,pin_pin_space,pin_pin_space_l,pos_start_x_l, top_qubit_id,low_qubit_id):
    pos_start_y_l = pos_start_y-int((pin_qubit_num)/2)*pin_pin_space+int((pin_qubit_num)/2)*pin_pin_space_l
    # pos_end_y_l = pos_end_y-(pin_qubit_num-1)*pin_pin_space_l
    for i in range(pin_qubit_num):
        otg = ShortToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r'+str(i),
                                            options=Dict(pos_x=pos_start_x_l,  pos_y=pos_start_y_l-i*pin_pin_space_l, orientation='180'))
        pin_qubit_list.append(otg)
    for i in range(pin_qubit_num):
        otg = ShortToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_l'+str(i),
                           options=Dict(pos_x=pos_start_x_l,  pos_y=pos_start_y_l-i*pin_pin_space_l, orientation='0'))
        pin_qubit_list.append(otg)


def  set_enlarged_readout_line_pins(pos_start_x_l, pin_pin_space_l, top_qubit_id,low_qubit_id,readout_id): # for qubit_num=8
    if top_qubit_id==19 :
        pin_qubit_list.append(ShortToGround(design, 'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_r', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_readout_line_l0'].parse_options().pos_y, orientation='180')))
        pin_qubit_list.append(ShortToGround(design,  'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_l', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_readout_line_l0'].parse_options().pos_y+pin_pin_space_l, orientation='0')))
    elif top_qubit_id==43:
        pin_qubit_list.append(ShortToGround(design, 'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_r', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_readout_line_r1'].parse_options().pos_y, orientation='180')))
        pin_qubit_list.append(ShortToGround(design,  'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_l', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_readout_line_r1'].parse_options().pos_y, orientation='0')))
    else:
        pin_qubit_list.append(ShortToGround(design, 'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_r', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r0'].parse_options().pos_y+pin_pin_space_l, orientation='180')))
        pin_qubit_list.append(ShortToGround(design,  'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_l', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r0'].parse_options().pos_y+pin_pin_space_l, orientation='0')))


#set the read line pins
readline_pos_y_list =[]
for i in [0,23,46,69]:
    readline_pos_y_list.append(design.components['R'+str(i)].pins.readout.middle[1]+(design.components['R'+str(i+5)].pins.readout.middle[1]-design.components['R'+str(i)].pins.readout.middle[1])/2)
for i in [21,44,67,90]:
    readline_pos_y_list.append(design.components['R'+str(i)].pins.readout.middle[1]+(design.components['R'+str(i-9)].pins.readout.middle[1]-design.components['R'+str(i)].pins.readout.middle[1])/2)
readline_pos_y_list.append(design.components['R92'].pins.readout.middle[1]+rr_space)

for i in range(len(readline_pos_y_list)):
    otg0 = ShortToGround(design, 'open_readout_line_l'+str(i), options=Dict(pos_x=pos_start_x,  pos_y=readline_pos_y_list[i], orientation='0'))
    otg0_r = ShortToGround(design, 'open_readout_line_l_rpin'+str(i), options=Dict(pos_x=pos_start_x,  pos_y=readline_pos_y_list[i], orientation='180'))
    otg1 = ShortToGround(design, 'open_readout_line_r'+str(i), options=Dict(pos_x=-pos_start_x,  pos_y=readline_pos_y_list[i], orientation='0'))
    otg1_r = ShortToGround(design, 'open_readout_line_r_rpin'+str(i), options=Dict(pos_x=-pos_start_x,  pos_y=readline_pos_y_list[i], orientation='180'))
    pin_qubit_list.append(otg0)
    pin_qubit_list.append(otg1)





pin_qubit_num0_r = 8
#1st section pins with sides and top wiring
set_side_pins(pos_start_x, pin_qubit_num0,65,56)
set_side_pins(pos_start_x_r,pin_qubit_num0_r,66,64)

#2nd section side pins
pin_qubit_num1 = 8
pin_qubit_num1_r = 8
pos_start_y,pos_end_y,pin_pin_space = set_side_pins(pos_start_x,pin_qubit_num1,67,24)

pos_start_y_r,pos_end_y_r,pin_pin_space_r = set_side_pins(pos_start_x_r,pin_qubit_num1_r,68,32)

# enlarge pins
enlarge_xspace = 1.5
enlarge_ratio = 2
pin_pin_length = abs(pos_start_y-pos_end_y)
pin_pin_length_l = pin_pin_length*enlarge_ratio
pin_pin_space_l = pin_pin_length_l/(pin_qubit_num1-1)
pos_start_x_l = pos_start_x-enlarge_xspace
set_enlarged_side_pins(pos_start_y, pin_qubit_num1,pin_pin_space,pin_pin_space_l,pos_start_x_l,67,24)
set_enlarged_readout_line_pins(pos_start_x_l,pin_pin_space_l,67,24,0)

pin_pin_space_l_r = pin_pin_length_l/(pin_qubit_num1_r-1)
pos_start_x_l_r = pos_start_x_r+enlarge_xspace
set_enlarged_side_pins(pos_start_y_r, pin_qubit_num1_r,pin_pin_space_r,pin_pin_space_l_r,pos_start_x_l_r,68,32)
set_enlarged_readout_line_pins(pos_start_x_l_r,pin_pin_space_l_r, 68,32,0)


#3rd section side pins
pin_qubit_num2 = 8
pin_qubit_num2_r = 9
pos_start_y,pos_end_y,pin_pin_space=set_side_pins(pos_start_x,pin_qubit_num2,42,33)

pos_start_y_r,pos_end_y_r,pin_pin_space_r = set_side_pins(pos_start_x_r,pin_qubit_num2_r,43,41)

#enlarge pins
pin_pin_space_l = pin_pin_length_l/(pin_qubit_num2-1)
set_enlarged_side_pins(pos_start_y,pin_qubit_num2,pin_pin_space,pin_pin_space_l,pos_start_x_l,42,33)
set_enlarged_readout_line_pins(pos_start_x_l,pin_pin_space_l,42,33,1)

pin_pin_space_l_r = pin_pin_length_l/(pin_qubit_num2_r-1)
set_enlarged_side_pins(pos_start_y_r, pin_qubit_num2_r,pin_pin_space_r,pin_pin_space_l_r,pos_start_x_l_r,43,41)
set_enlarged_readout_line_pins(pos_start_x_l_r,0, 43,41,1)

#fourth section side pins
pin_qubit_num3 = 8
pin_qubit_num3_r = 8
pos_start_y,pos_end_y,pin_pin_space=set_side_pins(pos_start_x,pin_qubit_num3,44,1)

pos_start_y_r,pos_end_y_r,pin_pin_space_r = set_side_pins(pos_start_x_r,pin_qubit_num3_r,45,9)

#enlarge pins
pin_pin_space_l = pin_pin_length_l/(pin_qubit_num3-1)
set_enlarged_side_pins(pos_start_y,pin_qubit_num3,pin_pin_space,pin_pin_space_l,pos_start_x_l,44,1)
set_enlarged_readout_line_pins(pos_start_x_l,pin_pin_space_l,44,1,2)

pin_pin_space_l_r = pin_pin_length_l/(pin_qubit_num3_r-1)
set_enlarged_side_pins(pos_start_y_r, pin_qubit_num3_r,pin_pin_space_r,pin_pin_space_l_r,pos_start_x_l_r,45,9)
set_enlarged_readout_line_pins(pos_start_x_l_r,pin_pin_space_l_r, 45,9,2)


# 5th section side pins
pin_qubit_num4 = 9
pin_qubit_num4_r = 8
pos_start_y,pos_end_y,pin_pin_space = set_side_pins(pos_start_x,pin_qubit_num4,19,10)

pos_start_y_r,pos_end_y_r,pin_pin_space_r = set_side_pins(pos_start_x_r,pin_qubit_num4_r,20,18)

#enlarge pins
pin_pin_space_l = pin_pin_length_l/(pin_qubit_num4-1)
set_enlarged_side_pins(pos_start_y,pin_qubit_num4,pin_pin_space,pin_pin_space_l,pos_start_x_l,19,10)
set_enlarged_readout_line_pins(pos_start_x_l,0,19,10,3)

pin_pin_space_l_r = pin_pin_length_l/(pin_qubit_num4_r-1)
set_enlarged_side_pins(pos_start_y_r, pin_qubit_num4_r,pin_pin_space_r,pin_pin_space_l_r,pos_start_x_l_r,20,18)
set_enlarged_readout_line_pins(pos_start_x_l_r,pin_pin_space_l_r, 20,18,3)

#6th section side pins
pin_qubit_num5 = 8
pin_qubit_num5_r =8
pos_start_y,pos_end_y,pin_pin_space = set_side_pins(pos_start_x,pin_qubit_num5,21,70)

pos_start_y_r,pos_end_y_r,pin_pin_space_r = set_side_pins(pos_start_x_r,pin_qubit_num5_r,22,78)


#enlarge pins
pin_pin_space_l = pin_pin_length_l/(pin_qubit_num5-1)
set_enlarged_side_pins(pos_start_y,pin_qubit_num5,pin_pin_space,pin_pin_space_l,pos_start_x_l,21,70)
set_enlarged_readout_line_pins(pos_start_x_l,pin_pin_space_l, 21,70,4)

pin_pin_space_l_r = pin_pin_length_l/(pin_qubit_num5_r-1)
set_enlarged_side_pins(pos_start_y_r, pin_qubit_num5_r,pin_pin_space_r,pin_pin_space_l_r,pos_start_x_l_r,22,78)
set_enlarged_readout_line_pins(pos_start_x_l_r,pin_pin_space_l_r, 22,78,4)

#7th section side pins
pin_qubit_num6 = 8
pin_qubit_num6_r = 9
pos_start_y,pos_end_y,pin_pin_space = set_side_pins(pos_start_x,pin_qubit_num6,88,79)

pin_qubit_list.append(ShortToGround(design, 'open_Q90', options=Dict(pos_x=pos_start_x,  pos_y=design.components['Q90'].parse_options().pos_y-pin_start_space, orientation='0')))
pin_qubit_list.append(ShortToGround(design, 'open_Q90_r', options=Dict(pos_x=pos_start_x,  pos_y=design.components['Q90'].parse_options().pos_y-pin_start_space, orientation='180')))

pos_start_y_r,pos_end_y_r,pin_pin_space_r = set_side_pins(pos_start_x_r,pin_qubit_num6_r,89,87)

pin_qubit_list.append(ShortToGround(design, 'open_Q91', options=Dict(pos_x=pos_start_x_r,  pos_y=design.components['Q91'].parse_options().pos_y-pin_start_space, orientation='0')))
pin_qubit_list.append(ShortToGround(design, 'open_Q91_r', options=Dict(pos_x=pos_start_x_r,  pos_y=design.components['Q91'].parse_options().pos_y-pin_start_space, orientation='180')))




# set the top pins for virtual wiring
top_vpin_list = []
top_vpin_launch_list = []
pad_pin_vspace =  1.5
top_pin_num =7
pin_for_side_num = 3
top_vpin_num = pin_qubit_num0+top_pin_num-pin_for_side_num+1

top_vpin_pos_y = design.components['launch_zline029'].parse_options().pos_y-pad_pin_vspace
top_vpin_start_pos_x = design.components['Q47'].parse_options().pos_x
top_vpin_end_pos_x = design.components['Q51'].parse_options().pos_x-0.1
top_vpin_space =abs( top_vpin_end_pos_x-top_vpin_start_pos_x)/(top_vpin_num-1)

for i in range(top_vpin_num):
    stg = ShortToGround(design, 'top_virtual'+str(i), options=Dict(pos_x=top_vpin_start_pos_x+i*top_vpin_space,  pos_y=top_vpin_pos_y, orientation='90'))
    stg1 = ShortToGround(design, 'top_virtual_r'+str(i), options=Dict(pos_x=-(top_vpin_start_pos_x+i*top_vpin_space),  pos_y=top_vpin_pos_y, orientation='90'))
    top_vpin_list.append(stg)
    top_vpin_list.append(stg1)
    stg2 = ShortToGround(design, 'top_virtual_l'+str(i), options=Dict(pos_x=top_vpin_start_pos_x+i*top_vpin_space,  pos_y=top_vpin_pos_y, orientation='-90'))
    stg3 = ShortToGround(design, 'top_virtual_l_r'+str(i), options=Dict(pos_x=-(top_vpin_start_pos_x+i*top_vpin_space),  pos_y=top_vpin_pos_y, orientation='-90'))
    top_vpin_launch_list.append(stg2)
    top_vpin_launch_list.append(stg3)


# for i in range(top_vpin_num):
#     stg = ShortToGround(design, 'top_virtual_l'+str(i), options=Dict(pos_x=top_vpin_start_pos_x+i*top_vpin_space,  pos_y=top_vpin_pos_y, orientation='-90'))
#     top_vpin_launch_list.append(stg)
low_vpin_num = top_vpin_num+2
low_vpin_pos_y = design.components['launch_zline113'].parse_options().pos_y+pad_pin_vspace-0.5
low_vpin_start_pos_x = design.components['Q92'].parse_options().pos_x
low_vpin_end_pos_x = design.components['Q96'].parse_options().pos_x-0.1
low_vpin_space =abs( low_vpin_end_pos_x-low_vpin_start_pos_x)/(low_vpin_num-1)
for i in range(low_vpin_num):
    stg = ShortToGround(design, 'low_virtual'+str(i), options=Dict(pos_x=low_vpin_start_pos_x+i*low_vpin_space,  pos_y=low_vpin_pos_y, orientation='-90'))
    stg1 = ShortToGround(design, 'low_virtual_r'+str(i), options=Dict(pos_x=-(low_vpin_start_pos_x+i*low_vpin_space),  pos_y=low_vpin_pos_y, orientation='-90'))
    top_vpin_list.append(stg)
    top_vpin_list.append(stg1)
    stg2 = ShortToGround(design, 'low_virtual_l'+str(i), options=Dict(pos_x=low_vpin_start_pos_x+i*low_vpin_space,  pos_y=low_vpin_pos_y, orientation='90'))
    stg3 = ShortToGround(design, 'low_virtual_l_r'+str(i), options=Dict(pos_x=-(low_vpin_start_pos_x+i*low_vpin_space),  pos_y=low_vpin_pos_y, orientation='90'))
    top_vpin_launch_list.append(stg2)
    top_vpin_launch_list.append(stg3)


gui.rebuild()
gui.autoscale()

# **********************************************************************************************************************************************************************************#
#wiring for inside pins for qubits Q47-Q51 (upper left)
# **********************************************************************************************************************************************************************************#

fillet_i = '50um'
fillet = '90um'
control_line_list = []
inside_pin_list = []
line_qubit_gap = 0.12
line_line_gap = 0.12

opt = Dict(pos_x=design.components['Q'+str(47)].options.pos_x, pos_y=design.components['Q'+str(47)].options.pos_y ,
           inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
control_line_list.append( MyFluxLine02(design,'flux_line'+str(47),options=opt))
#
#
jogsS = OrderedDict()
# jogsS[0] = ["R", str(1.25)+'mm']
jogsS[0] = ["R", '100um']
# jogsS[2] = ["L", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(47),pin='flux_pin'),
                         end_pin=Dict(component='top_virtual'+str(7),pin='short'),),lead = Dict(start_straight=1.25,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(47)+'_top_virtual'+str(7),options=pin_opt))
#
#
opt = Dict(pos_x=design.components['Q'+str(47)].parse_options().pos_x+location_x,
                       pos_y=design.components['Q'+str(47)].parse_options().pos_y,
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '0',
                       # fillet = '1 um',
                       orientation='90',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(47),options=opt))

jogsS = OrderedDict()
# jogsS[0] = ["R", str(1.25-0.25)+'mm']
jogsS[0] = ["R", '100um']
# jogsS[2] = ["L", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(47),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual'+str(8),pin='short'),),lead = Dict(start_straight=1.25-0.25,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(47)+'_top_virtual'+str(8),options=pin_opt))

#--------------------------------------------------------------------------------------------------------------------------------------------------
opt = Dict(pos_x=design.components['Q'+str(48)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(48)].parse_options().pos_y+location_x,
                       l_1 = '400 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(48),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(48),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual'+str(9),pin='short'),),lead = Dict(start_straight=1.25-0.25*2-0.05,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(48)+'_top_virtual'+str(9),options=pin_opt))

#---------------------------------------------------------------------------------------------------------------------------------------------------------

opt = Dict(pos_x=design.components['Q'+str(49)].options.pos_x, pos_y=design.components['Q'+str(49)].options.pos_y ,
           inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
control_line_list.append( MyFluxLine02(design,'flux_line'+str(49),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(49),pin='flux_pin'),
                         end_pin=Dict(component='top_virtual'+str(10),pin='short'),),lead = Dict(start_straight=1.25-0.25*2,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(49)+'_top_virtual'+str(10),options=pin_opt))

opt = Dict(pos_x=design.components['Q'+str(49)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(49)].parse_options().pos_y+location_x,
                       l_1 = '200 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = False,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(49),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(49),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual'+str(11),pin='short'),),lead = Dict(start_straight=1.25-0.25*3-0.1,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(49)+'_top_virtual'+str(11),options=pin_opt))


#--------------------------------------------------------------------------------------------------------------------------------------------------------------

opt = Dict(pos_x=design.components['Q'+str(50)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(50)].parse_options().pos_y+location_x,
                       l_1 = '200 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = False,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(50),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(50),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual'+str(12),pin='short'),),lead = Dict(start_straight=1.25-0.25*3-0.1*2-0.07,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(50)+'_top_virtual'+str(12),options=pin_opt))

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

opt = Dict(pos_x=design.components['Q'+str(51)].options.pos_x, pos_y=design.components['Q'+str(51)].options.pos_y ,
           inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
control_line_list.append( MyFluxLine02(design,'flux_line'+str(51),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(51),pin='flux_pin'),
                         end_pin=Dict(component='top_virtual'+str(13),pin='short'),),lead = Dict(start_straight=0.01,
                         end_straight = 0.4,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(51)+'_top_virtual'+str(13),options=pin_opt))


# **********************************************************************************************************************************************************************************#
#wiring for inside pins for qubits Q51-Q55 (upper right)
# **********************************************************************************************************************************************************************************#



opt = Dict(pos_x=design.components['Q'+str(55)].options.pos_x, pos_y=design.components['Q'+str(55)].options.pos_y ,
           inverse = True, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
control_line_list.append( MyFluxLine02(design,'flux_line'+str(55),options=opt))
#
#
jogsS = OrderedDict()
# jogsS[0] = ["R", str(1.25)+'mm']
jogsS[0] = ["L", '100um']
# jogsS[2] = ["L", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(55),pin='flux_pin'),
                         end_pin=Dict(component='top_virtual_r'+str(6),pin='short'),),lead = Dict(start_straight=1.45,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(55)+'_top_virtual_r'+str(6),options=pin_opt))
#
#
opt = Dict(pos_x=design.components['Q'+str(55)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(55)].parse_options().pos_y+location_x,
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '1 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(55),options=opt))
#

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(55),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual_r'+str(7),pin='short'),),lead = Dict(start_straight=1.25-0.25,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(55)+'_top_virtual_r'+str(7),options=pin_opt))
#
# #--------------------------------------------------------------------------------------------------------------------------------------------------
opt = Dict(pos_x=design.components['Q'+str(54)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(54)].parse_options().pos_y+location_x,
                       l_1 = '400 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = False,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(54),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(54),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual_r'+str(8),pin='short'),),lead = Dict(start_straight=1.25-0.25*2+0.05,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(54)+'_top_virtual_r'+str(8),options=pin_opt))
#
# #---------------------------------------------------------------------------------------------------------------------------------------------------------
#
opt = Dict(pos_x=design.components['Q'+str(53)].options.pos_x, pos_y=design.components['Q'+str(53)].options.pos_y ,
           inverse = True, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
control_line_list.append( MyFluxLine02(design,'flux_line'+str(53),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(53),pin='flux_pin'),
                         end_pin=Dict(component='top_virtual_r'+str(9),pin='short'),),lead = Dict(start_straight=1.25-0.25*2+0.05,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(53)+'_top_virtual_r'+str(9),options=pin_opt))
#
opt = Dict(pos_x=design.components['Q'+str(53)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(53)].parse_options().pos_y+location_x,
                       l_1 = '200 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(53),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(53),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual_r'+str(10),pin='short'),),lead = Dict(start_straight=1.25-0.25*3-0.1,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(53)+'_top_virtual_r'+str(10),options=pin_opt))
#
#
# #--------------------------------------------------------------------------------------------------------------------------------------------------------------
l_1 =abs(design.components['Q'+str(52)].parse_options().pos_x-design.components['top_virtual_r'+str(11)].parse_options().pos_x)
opt = Dict(pos_x=design.components['Q'+str(52)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(52)].parse_options().pos_y+location_x,
                       l_1 = l_1,
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(52),options=opt))
#
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(52),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual_r'+str(11),pin='short'),),lead = Dict(start_straight=0.01,
                         end_straight = 0.1,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(52)+'_top_virtual_r'+str(11),options=pin_opt))
#
# #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#

opt = Dict(pos_x=design.components['Q'+str(51)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(51)].parse_options().pos_y+location_x,
                       l_1 = '200um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = False,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(51),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(51),pin='xy_pin'),
                         end_pin=Dict(component='top_virtual_r'+str(12),pin='short'),),lead = Dict(start_straight=0.01,
                         end_straight = 0.4,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(51)+'_top_virtual_r'+str(12),options=pin_opt))


# **********************************************************************************************************************************************************************************#
#wiring for inside pins for qubits Q92-Q96 (lower left)
# **********************************************************************************************************************************************************************************#

qubit_hw = design.components['Q92'].parse_options().cross_width/2

opt = Dict(pos_x=design.components['Q'+str(92)].options.pos_x, pos_y=design.components['Q'+str(92)].options.pos_y ,
           inverse = False, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')

control_line_list.append( MyFluxLine02(design,'flux_line'+str(92),options=opt))
#
#
jogsS = OrderedDict()
# jogsS[0] = ["R", str(1.25)+'mm']
jogsS[0] = ["L", '100um']
# jogsS[2] = ["L", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(92),pin='flux_pin'),
                         end_pin=Dict(component='low_virtual'+str(8),pin='short'),),lead = Dict(start_straight=1+line_line_gap,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(92)+'_low_virtual'+str(8),options=pin_opt))
#
#
opt = Dict(pos_x=design.components['Q'+str(92)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(92)].parse_options().pos_y-location_x,
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '1 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(92),options=opt))


pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(92),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual'+str(9),pin='short'),),lead = Dict(start_straight=1-location_x+0.1,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(92)+'_low_virtual'+str(9),options=pin_opt))
#
# #--------------------------------------------------------------------------------------------------------------------------------------------------
opt = Dict(pos_x=design.components['Q'+str(93)].parse_options().pos_x-location_x,
                       pos_y=design.components['Q'+str(93)].parse_options().pos_y,
                       l_1 = '200 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '0',
                       # fillet = '2.4 um',
                       orientation='90',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(93),options=opt))
#
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(93),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual'+str(10),pin='short'),),lead = Dict(start_straight=1-2*line_line_gap,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(93)+'_low_virtual'+str(10),options=pin_opt))
#
# #---------------------------------------------------------------------------------------------------------------------------------------------------------
#
opt = Dict(pos_x=design.components['Q'+str(94)].options.pos_x, pos_y=design.components['Q'+str(94)].options.pos_y ,
           inverse = False, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
control_line_list.append( MyFluxLine02(design,'flux_line'+str(94),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(94),pin='flux_pin'),
                         end_pin=Dict(component='low_virtual'+str(11),pin='short'),),lead = Dict(start_straight=1-3*line_line_gap+0.03,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(94)+'_low_virtual'+str(11),options=pin_opt))
# #
opt = Dict(pos_x=design.components['Q'+str(94)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(94)].parse_options().pos_y-location_x,
                       l_1 = '400 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(94),options=opt))
# #
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(94),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual'+str(12),pin='short'),),lead = Dict(start_straight=1-6*line_line_gap+0.03,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(94)+'_low_virtual'+str(12),options=pin_opt))
#
#
# #--------------------------------------------------------------------------------------------------------------------------------------------------------------
#
opt = Dict(pos_x=design.components['Q'+str(95)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(95)].parse_options().pos_y-location_x,
                       l_1 = '100 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '0',
                       # fillet = '1 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(95),options=opt))
# #
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(95),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual'+str(13),pin='short'),),lead = Dict(start_straight=0.01,
                         end_straight = 0.1,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(95)+'_low_virtual'+str(13),options=pin_opt))
#
# #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#
opt = Dict(pos_x=design.components['Q'+str(96)].options.pos_x, pos_y=design.components['Q'+str(96)].options.pos_y ,
           inverse = False, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45')

control_line_list.append( MyFluxLine02(design,'flux_line'+str(96),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(96),pin='flux_pin'),
                         end_pin=Dict(component='low_virtual'+str(14),pin='short'),),lead = Dict(start_straight=0.01,
                         end_straight = 0.4,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(96)+'_low_virtual'+str(14),options=pin_opt))

# **********************************************************************************************************************************************************************************#
#wiring for inside pins for qubits Q96-Q100 (lower right)
# **********************************************************************************************************************************************************************************#

opt = Dict(pos_x=design.components['Q'+str(100)].options.pos_x, pos_y=design.components['Q'+str(100)].options.pos_y ,
           inverse = False, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')

control_line_list.append( MyFluxLine02(design,'flux_line'+str(100),options=opt))
#
#
jogsS = OrderedDict()
# jogsS[0] = ["R", str(1.25)+'mm']
jogsS[0] = ["R", '100um']
# jogsS[2] = ["L", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(100),pin='flux_pin'),
                         end_pin=Dict(component='low_virtual_r'+str(8),pin='short'),),lead = Dict(start_straight=1,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(100)+'_low_virtual_r'+str(8),options=pin_opt))
# #
# #
opt = Dict(pos_x=design.components['Q'+str(100)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(100)].parse_options().pos_y-location_x,
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '1 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = False,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(100),options=opt))
#
#
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(100),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual_r'+str(9),pin='short'),),lead = Dict(start_straight=1-location_x+0.1-line_line_gap+0.03,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(100)+'_low_virtual_r'+str(9),options=pin_opt))
# #
# # #--------------------------------------------------------------------------------------------------------------------------------------------------
opt = Dict(pos_x=design.components['Q'+str(99)].parse_options().pos_x-location_x,
                       pos_y=design.components['Q'+str(99)].parse_options().pos_y,
                       l_1 = '200 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '0',
                       # fillet = '2.4 um',
                       orientation='90',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(99),options=opt))
# #
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(99),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual_r'+str(10),pin='short'),),lead = Dict(start_straight=1-3*line_line_gap+0.03,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(99)+'_low_virtual_r'+str(10),options=pin_opt))
# #
# # #---------------------------------------------------------------------------------------------------------------------------------------------------------
# #
opt = Dict(pos_x=design.components['Q'+str(98)].options.pos_x, pos_y=design.components['Q'+str(98)].options.pos_y ,
           inverse = False, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
control_line_list.append( MyFluxLine02(design,'flux_line'+str(98),options=opt))
#
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(98),pin='flux_pin'),
                         end_pin=Dict(component='low_virtual_r'+str(11),pin='short'),),lead = Dict(start_straight=1-4*line_line_gap+0.03+0.03,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(98)+'_low_virtual_r'+str(11),options=pin_opt))
# # #
opt = Dict(pos_x=design.components['Q'+str(98)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(98)].parse_options().pos_y-location_x,
                       l_1 = '400 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '2.4 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = False,
                       subtract=True,
                       chip='main',
                     )
control_line_list.append(MyXYLine01(design,'xy_line'+str(98),options=opt))
# # #
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(98),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual_r'+str(12),pin='short'),),lead = Dict(start_straight=1-7*line_line_gap+0.03+0.03+0.02,
                         end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(98)+'_low_virtual_r'+str(12),options=pin_opt))
# #
# #
# # #--------------------------------------------------------------------------------------------------------------------------------------------------------------
# #
opt = Dict(pos_x=design.components['Q'+str(97)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(97)].parse_options().pos_y-location_x,
                       l_1 = '100 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '0',
                       # fillet = '1 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = False,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(97),options=opt))
# # #
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(97),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual_r'+str(13),pin='short'),),lead = Dict(start_straight=0.01,
                         end_straight = 0.1,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(97)+'_low_virtual_r'+str(13),options=pin_opt))
# #
# # #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
# #
opt = Dict(pos_x=design.components['Q'+str(96)].parse_options().pos_x,
                       pos_y=design.components['Q'+str(96)].parse_options().pos_y-location_x,
                       l_1 = '100 um',
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '0',
                       # fillet = '1 um',
                       orientation='180',
                       layer='1',
                       layer_subtract='1',
                       inverse = True,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )

control_line_list.append(MyXYLine01(design,'xy_line'+str(96),options=opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(96),pin='xy_pin'),
                         end_pin=Dict(component='low_virtual_r'+str(14),pin='short'),),lead = Dict(start_straight=0.01,
                         end_straight = 0.1,), fillet=fillet_i, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(96)+'_low_virtual_r'+str(14),options=pin_opt))


# **********************************************************************************************************************************************************************************#
# wiring for inside side pins of type 1 (left side)
# **********************************************************************************************************************************************************************************#

def routing_inside_pins(side_pin_num, start_qubit_id,end_qubit_id):
        """wiring for inside side pins of type 1

        Args:
            side_pin_num: The num of  side pins ,must be 8 or 9 now.
            start_qubit_id: The id of side start qubit for marking.
            end_qubit_id: The id of side end qubit for marking.


        Raises:
            ValueError: side_pin_num is not 8 or 9

        """
        if side_pin_num not in [8,9]:
            raise ValueError("Error: please input side_pin_num 8 or 9, other values are not supported")

        flux_y_pos = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1)].parse_options().pos_y-design.components['Q'+str(end_qubit_id)].parse_options().pos_y)


        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id)].options.pos_y ,
                   inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45',end_yposition =flux_y_pos)

        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(end_qubit_id),pin='flux_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-1),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(end_qubit_id)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-1),options=pin_opt))

        xy_y_pos = design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2)].parse_options().pos_y

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].parse_options().pos_x,
                               pos_y=xy_y_pos,
                               # l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )

        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(end_qubit_id),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-2),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(end_qubit_id)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-2),options=pin_opt))

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        xy_y_pos = design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3)].parse_options().pos_y

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+1)].parse_options().pos_x,
                               pos_y=xy_y_pos,
                               # l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id+1),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(end_qubit_id+1),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-3),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(end_qubit_id+1)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-3),options=pin_opt))


        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #end connection for Q65 as reference

        opt = Dict(pos_x=design.components['Q'+str(start_qubit_id)].parse_options().pos_x-location_x,
                               pos_y=design.components['Q'+str(start_qubit_id)].parse_options().pos_y,
                               l_1 = abs(design.components['Q'+str(start_qubit_id)].parse_options().pos_y-design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(0)].parse_options().pos_y),
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '1 um',
                               orientation='90',
                               layer='1',
                               layer_subtract='1',
                               inverse = True,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(start_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(start_qubit_id),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(0),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(start_qubit_id)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(0),options=pin_opt))

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+2)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id+2)].options.pos_y ,
                   inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id+2),options=opt))

        #$$$$$$$$$$$$$$$$$---------------------------------------------------complex routing----------------------------------------------------------------------------$$$$$$$$$$$$$$$$$

        start_straight = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-4)].parse_options().pos_x - design.components['Q'+str(end_qubit_id+1)].parse_options().pos_x)

        jogsS = OrderedDict()
        # jogsS[0] = ["R", str(1.25)+'mm']
        jogsS[0] = ["L", '400um']
        # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-4),pin='short'),
                                 end_pin=Dict(component='flux_line'+str(end_qubit_id+2),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-4)+'_flux_line'+str(end_qubit_id+2),options=pin_opt))

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+2)].parse_options().pos_x+location_x,
                               pos_y=design.components['Q'+str(end_qubit_id+2)].parse_options().pos_y,
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='90',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id+2),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-5),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id+2),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-5)+'_xy_line'+str(end_qubit_id+2),options=pin_opt))


        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+3)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id+3)].parse_options().pos_y+location_x,
                               l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '2.4 um',
                               orientation='180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id+3),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-6),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id+3),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*2,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-6)+'_xy_line'+str(end_qubit_id+3),options=pin_opt))

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+4)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id+4)].options.pos_y ,
                   inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45')
        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id+4),options=opt))


        jogsE = OrderedDict()
        # jogsS[0] = ["R", str(1.25)+'mm']
        jogsE[0] = ["R", '100um']
        # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7),pin='short'),
                                 end_pin=Dict(component='flux_line'+str(end_qubit_id+4),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*3,
                                 end_straight = 0.68,start_jogged_extension=jogsS,end_jogged_extension=jogsE), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7)+'_flux_line'+str(end_qubit_id+4),options=pin_opt))

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if (side_pin_num==9):
                opt = Dict(pos_x=design.components['Q'+str(start_qubit_id-19)].parse_options().pos_x-location_x,
                                       pos_y=design.components['Q'+str(start_qubit_id-19)].parse_options().pos_y,
                                       # l_1 = abs(design.components['Q'+str(65)].parse_options().pos_y-design.components['open_Q'+str(65)+'_Q'+str(56)+'_'+str(0)].parse_options().pos_y),
                                       flux_cpw_width='5 um',
                                       flux_cpw_gap='3 um',
                                       flux_cpw_width0='10 um',
                                       flux_cpw_gap0='5um',
                                       c_length = '15 um',
                                       angle = '90',
                                       # fillet = '1 um',
                                       orientation='90',
                                       layer='1',
                                       layer_subtract='1',
                                       inverse = True,
                                       mirror = True,
                                       subtract=True,
                                       chip='main',
                                     )
                control_line_list.append(MyXYLine01(design,'xy_line'+str(start_qubit_id-19),options=opt))

                pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-8),pin='short'),
                                         end_pin=Dict(component='xy_line'+str(start_qubit_id-19),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*4,
                                         end_straight = 0.26,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

                inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-8)+'_xy_line'+str(start_qubit_id-19),options=pin_opt))

routing_inside_pins(side_pin_num=9,start_qubit_id=65,end_qubit_id=56)
routing_inside_pins(side_pin_num=8,start_qubit_id=42,end_qubit_id=33)
routing_inside_pins(side_pin_num=9,start_qubit_id=19,end_qubit_id=10)
routing_inside_pins(side_pin_num=8,start_qubit_id=88,end_qubit_id=79)

# **********************************************************************************************************************************************************************************#
# wiring for inside side pins of type 1 (right side)
# **********************************************************************************************************************************************************************************#

def routing_inside_pins_rhs(side_pin_num, start_qubit_id,end_qubit_id):
        """wiring for inside side pins of type 1 on right hand side

        Args:
            side_pin_num: The num of  side pins ,must be 8 or 9 now.
            start_qubit_id: The id of side start qubit for marking.
            end_qubit_id: The id of side end qubit for marking.


        Raises:
            ValueError: side_pin_num is not 8 or 9

        """
        if side_pin_num not in [8,9]:
            raise ValueError("Error: please input side_pin_num 8 or 9, other values are not supported")

        flux_y_pos = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1)].parse_options().pos_y-design.components['Q'+str(end_qubit_id)].parse_options().pos_y)


        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id)].options.pos_y ,
                   inverse = True, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45',end_yposition =flux_y_pos)

        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id),options=opt))


        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(end_qubit_id),pin='flux_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(end_qubit_id)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1),options=pin_opt))

        xy_y_pos = design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2)].parse_options().pos_y

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].parse_options().pos_x,
                               pos_y=xy_y_pos,
                               # l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )

        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(end_qubit_id),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(end_qubit_id)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2),options=pin_opt))

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        xy_y_pos = design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3)].parse_options().pos_y

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-1)].parse_options().pos_x,
                               pos_y=xy_y_pos,
                               # l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-1),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(end_qubit_id-1),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(end_qubit_id-1)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3),options=pin_opt))


        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


        opt = Dict(pos_x=design.components['Q'+str(start_qubit_id)].parse_options().pos_x,
                               pos_y=design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(0)].parse_options().pos_y,
                               # l_1 = abs(design.components['Q'+str(start_qubit_id)].parse_options().pos_y-design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(0)].parse_options().pos_y),
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='0',
                               layer='1',
                               layer_subtract='1',
                               inverse = True,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(start_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(start_qubit_id),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(0),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(start_qubit_id)+'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(0),options=pin_opt))
        #
        # #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-2)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id-2)].options.pos_y ,
                   inverse = True, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id-2),options=opt))
        #
        # #$$$$$$$$$$$$$$$$$---------------------------------------------------complex routing----------------------------------------------------------------------------$$$$$$$$$$$$$$$$$
        #
        start_straight = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-4)].parse_options().pos_x - design.components['Q'+str(end_qubit_id-1)].parse_options().pos_x)

        jogsS = OrderedDict()
        # jogsS[0] = ["R", str(1.25)+'mm']
        jogsS[0] = ["R", '250um']
        # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-4),pin='short'),
                                 end_pin=Dict(component='flux_line'+str(end_qubit_id-2),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-4)+'_flux_line'+str(end_qubit_id-2),options=pin_opt))
        #
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-2)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id-2)].parse_options().pos_y+location_x,
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '1 um',
                               orientation='0',
                               layer='1',
                               layer_subtract='1',
                               inverse = True,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-2),options=opt))
        #
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-5),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id-2),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-5)+'_xy_line'+str(end_qubit_id-2),options=pin_opt))
        #
        #
        # #--------------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-3)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id-3)].parse_options().pos_y+location_x,
                               l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '1 um',
                               orientation='180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-3),options=opt))
        #
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-6),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id-3),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*2,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-6)+'_xy_line'+str(end_qubit_id-3),options=pin_opt))

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-4)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id-4)].parse_options().pos_y+location_x,
                               l_1 = '400 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '1 um',
                               orientation='180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-4),options=opt))
        #

        jogsE = OrderedDict()

        jogsE[0] = ["R", '0.95 mm']
        jogsE[1] = ["L", '100 um']


        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-7),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id-4),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*3,
                                 end_straight = 0.35,start_jogged_extension=jogsS, end_jogged_extension=jogsE), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-7)+'_xy_line'+str(end_qubit_id-4),options=pin_opt))


        # opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+4)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id+4)].options.pos_y ,
        #            inverse = True, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45')
        # control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id+4),options=opt))
        #
        #
        # jogsE = OrderedDict()
        # # jogsS[0] = ["R", str(1.25)+'mm']
        # jogsE[0] = ["L", '100um']
        # # jogsS[2] = ["L", '100um']
        #
        # pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7),pin='short'),
        #                          end_pin=Dict(component='flux_line'+str(end_qubit_id+4),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*3,
        #                          end_straight = 0.68,start_jogged_extension=jogsS,end_jogged_extension=jogsE), fillet=fillet_i, chip = 'main')
        #
        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7)+'_flux_line'+str(end_qubit_id+4),options=pin_opt))

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if (side_pin_num==9):
                opt = Dict(pos_x=design.components['Q'+str(start_qubit_id-20)].parse_options().pos_x,
                                       pos_y=design.components['Q'+str(start_qubit_id-20)].parse_options().pos_y-location_x+0.1,
                                       # l_1 = abs(design.components['Q'+str(65)].parse_options().pos_y-design.components['open_Q'+str(65)+'_Q'+str(56)+'_'+str(0)].parse_options().pos_y),
                                       flux_cpw_width='5 um',
                                       flux_cpw_gap='3 um',
                                       flux_cpw_width0='10 um',
                                       flux_cpw_gap0='5um',
                                       c_length = '15 um',
                                       angle = '0',
                                       # fillet = '1 um',
                                       orientation='180',
                                       layer='1',
                                       layer_subtract='1',
                                       inverse = True,
                                       mirror = True,
                                       subtract=True,
                                       chip='main',
                                     )
                control_line_list.append(MyXYLine01(design,'xy_line'+str(start_qubit_id-20),options=opt))

                pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-8),pin='short'),
                                         end_pin=Dict(component='xy_line'+str(start_qubit_id-20),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*4,
                                         end_straight = 0.26+0.36,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

                inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-8)+'_xy_line'+str(start_qubit_id-19),options=pin_opt))

routing_inside_pins_rhs(side_pin_num=8,start_qubit_id=66,end_qubit_id=64)
routing_inside_pins_rhs(side_pin_num=9,start_qubit_id=43,end_qubit_id=41)
routing_inside_pins_rhs(side_pin_num=8,start_qubit_id=20,end_qubit_id=18)
routing_inside_pins_rhs(side_pin_num=9,start_qubit_id=89,end_qubit_id=87)


# **********************************************************************************************************************************************************************************#
# wiring for inside side pins of type 2 (left side)
# **********************************************************************************************************************************************************************************#

def routing_inside_pins_beta(side_pin_num, start_qubit_id,end_qubit_id):
        """wiring for inside side pins of type 2

        Args:
            side_pin_num: The num of  side pins ,must be 8  now.
            start_qubit_id: The id of side start qubit for marking.
            end_qubit_id: The id of side end qubit for marking.


        Raises:
            ValueError: side_pin_num is not 8 or 9

        """
        if side_pin_num not in [8]:
                raise ValueError("Error: please input side_pin_num 8 , other values are not supported now")

        flux_y_pos = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1)].parse_options().pos_y-design.components['Q'+str(end_qubit_id)].parse_options().pos_y)

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id)].options.pos_y ,
                   inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45',end_yposition =flux_y_pos)
        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(end_qubit_id),pin='flux_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-1),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(start_qubit_id)+'open_Q'+str(end_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-1),options=pin_opt))

        xy_y_pos = design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2)].parse_options().pos_y

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].parse_options().pos_x,
                               pos_y=xy_y_pos,
                               # l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(end_qubit_id),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-2),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(start_qubit_id)+'open_Q'+str(end_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-2),options=pin_opt))

        #-----------------------------------------------------------------complex routing-----------------------------------------------------------------------------------------
        line_qubit_gap = 0.12
        line_line_gap = 0.12
        start_straight = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3)].parse_options().pos_x - design.components['Q'+str(end_qubit_id)].parse_options().pos_x)

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+1)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id+1)].parse_options().pos_y+location_x,
                               l_1 = '400 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '1 um',
                               orientation='180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id+1),options=opt))


        jogsS = OrderedDict()
        # jogsS[0] = ["R", str(1.25)+'mm']
        jogsS[0] = ["L", '250um']
        # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-3),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id+1),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-3)+'_xy_line'+str(end_qubit_id+1),options=pin_opt))


        #------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+2)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id+2)].options.pos_y ,
                   inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45',end_yposition =flux_y_pos)

        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id+2),options=opt))

        # jogsS = OrderedDict()
        # # jogsS[0] = ["R", str(1.25)+'mm']
        # jogsS[0] = ["L", '400um']
        # # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-4),pin='short'),
                                 end_pin=Dict(component='flux_line'+str(end_qubit_id+2),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap,
                                 end_straight = 0.95,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-4)+'_flux_line'+str(end_qubit_id+2),options=pin_opt))


        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+2)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id+2)].parse_options().pos_y+location_x+0.1,
                               # l_1 = '400 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id+2),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-5),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id+2),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*2,
                                 end_straight = 0.65,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-5)+'_xy_line'+str(end_qubit_id+2),options=pin_opt))

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+3)].parse_options().pos_x-location_x,
                               pos_y=design.components['Q'+str(end_qubit_id+3)].parse_options().pos_y,
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='90',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )

        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id+3),options=opt))


        jogsS[1] = ["R", str(2.27)+'mm']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-6),pin='short'),
                                  end_pin=Dict(component='xy_line'+str(end_qubit_id+3),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*3,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-6)+'_xy_line'+str(end_qubit_id+3),options=pin_opt))


        #------------------------------------------------------------------------------------------------------------------------------------------------------------

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id+4)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id+4)].options.pos_y ,
                   inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id+4),options=opt))

        jogsS[1] = ["R", str(2.27+0.13*2)+'mm']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7),pin='short'),
                                 end_pin=Dict(component='flux_line'+str(end_qubit_id+4),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*4,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7)+'_flux_line'+str(end_qubit_id+4),options=pin_opt))

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------

        opt = Dict(pos_x=design.components['Q'+str(start_qubit_id)].parse_options().pos_x-location_x,
                               pos_y=design.components['Q'+str(start_qubit_id)].parse_options().pos_y,
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '-90',
                               # fillet = '1 um',
                               orientation='90',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )


        control_line_list.append(MyXYLine01(design,'xy_line'+str(start_qubit_id),options=opt))

        jogsS = OrderedDict()
        # jogsS[0] = ["R", str(1.25)+'mm']
        jogsS[0] = ["L", '250um']
        # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(0),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(start_qubit_id),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*5,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(0)+'_xy_line'+str(start_qubit_id),options=pin_opt))

routing_inside_pins_beta(side_pin_num=8,start_qubit_id=67,end_qubit_id=24)
routing_inside_pins_beta(side_pin_num=8,start_qubit_id=44,end_qubit_id=1)
routing_inside_pins_beta(side_pin_num=8,start_qubit_id=21,end_qubit_id=70)


# **********************************************************************************************************************************************************************************#
# wiring for inside side pins of type 2 (right side)
# **********************************************************************************************************************************************************************************#


def routing_inside_pins_beta_rhs(side_pin_num, start_qubit_id,end_qubit_id):
        """wiring for inside side pins of type 2

        Args:
            side_pin_num: The num of  side pins ,must be 8  now.
            start_qubit_id: The id of side start qubit for marking.
            end_qubit_id: The id of side end qubit for marking.


        Raises:
            ValueError: side_pin_num is not 8 or 9

        """
        if side_pin_num not in [8]:
                raise ValueError("Error: please input side_pin_num 8 , other values are not supported now")

        flux_y_pos = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1)].parse_options().pos_y-design.components['Q'+str(end_qubit_id)].parse_options().pos_y)

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id)].options.pos_y ,
                   inverse = True, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45',end_yposition =flux_y_pos)
        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id),options=opt))

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='flux_line'+str(end_qubit_id),pin='flux_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'flux_line'+str(start_qubit_id)+'open_Q'+str(end_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-1),options=pin_opt))

        xy_y_pos = design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2)].parse_options().pos_y

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id)].parse_options().pos_x,
                               pos_y=xy_y_pos,
                               # l_1 = '200 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id),options=opt))
        #
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='xy_line'+str(end_qubit_id),pin='xy_pin'),
                                 end_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2),pin='short'),), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'xy_line'+str(start_qubit_id)+'open_Q'+str(end_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-2),options=pin_opt))
        #
        # #-----------------------------------------------------------------complex routing-----------------------------------------------------------------------------------------

        start_straight = abs(design.components['open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3)].parse_options().pos_x - design.components['Q'+str(end_qubit_id)].parse_options().pos_x)

        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-1)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id-1)].parse_options().pos_y+location_x,
                               l_1 = '400 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '1 um',
                               orientation='180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-1),options=opt))
        #
        #
        jogsS = OrderedDict()
        # jogsS[0] = ["R", str(1.25)+'mm']
        jogsS[0] = ["R", '250um']
        # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id-1),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-3)+'_xy_line'+str(end_qubit_id-1),options=pin_opt))
        #
        #
        # #------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-2)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id-2)].options.pos_y ,
                   inverse = True, mirror = False, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '-45',end_yposition =flux_y_pos)

        control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id-2),options=opt))
        #
        # # jogsS = OrderedDict()
        # # # jogsS[0] = ["R", str(1.25)+'mm']
        # # jogsS[0] = ["L", '400um']
        # # # jogsS[2] = ["L", '100um']
        #
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-4),pin='short'),
                                 end_pin=Dict(component='flux_line'+str(end_qubit_id-2),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap,
                                 end_straight = 0.95,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-4)+'_flux_line'+str(end_qubit_id-2),options=pin_opt))
        #
        #
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-2)].parse_options().pos_x,
                               pos_y=design.components['Q'+str(end_qubit_id-2)].parse_options().pos_y+location_x+0.1,
                               # l_1 = '400 um',
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='180',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )
        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-2),options=opt))
        #
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-5),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(end_qubit_id-2),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*2,
                                 end_straight = 0.65,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-5)+'_xy_line'+str(end_qubit_id-2),options=pin_opt))
        #
        # #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-3)].parse_options().pos_x+location_x,
                               pos_y=design.components['Q'+str(end_qubit_id-3)].parse_options().pos_y,
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-90',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )

        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-3),options=opt))
        #
        #
        jogsS[1] = ["L", str(2.27)+'mm']
        jogsS[2] = ["L", '500um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-6),pin='short'),
                                  end_pin=Dict(component='xy_line'+str(end_qubit_id-3),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*3,
                                 end_straight = 0.18,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-6)+'_xy_line'+str(end_qubit_id-3),options=pin_opt))
        #
        #
        # #------------------------------------------------------------------------------------------------------------------------------------------------------------
        opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-4)].parse_options().pos_x+location_x,
                               pos_y=design.components['Q'+str(end_qubit_id-4)].parse_options().pos_y,
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '0',
                               # fillet = '1 um',
                               orientation='-90',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = False,
                               subtract=True,
                               chip='main',
                             )

        control_line_list.append(MyXYLine01(design,'xy_line'+str(end_qubit_id-4),options=opt))


        jogsS[1] = ["L", str(2.27+0.13*2)+'mm']
        # jogsS[2] = ["L", '500um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-7),pin='short'),
                                  end_pin=Dict(component='xy_line'+str(end_qubit_id-4),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*4,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(side_pin_num-7)+'_xy_line'+str(end_qubit_id-4),options=pin_opt))
        # #
        # opt = Dict(pos_x=design.components['Q'+str(end_qubit_id-4)].options.pos_x, pos_y=design.components['Q'+str(end_qubit_id-4)].options.pos_y ,
        #            inverse = True, mirror = True, end_horizontal_length = '20 um', flux_cpw_gap0='5 um',angle = '-45',angle_end = '45')
        # control_line_list.append( MyFluxLine02(design,'flux_line'+str(end_qubit_id+4),options=opt))
        #
        # jogsS[1] = ["R", str(2.27+0.13*2)+'mm']
        #
        # pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7),pin='short'),
        #                          end_pin=Dict(component='flux_line'+str(end_qubit_id+4),pin='flux_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*4,
        #                          end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')
        #
        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_rhs'+str(side_pin_num-7)+'_flux_line'+str(end_qubit_id+4),options=pin_opt))
        #
        # #-----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #
        opt = Dict(pos_x=design.components['Q'+str(start_qubit_id)].parse_options().pos_x+location_x,
                               pos_y=design.components['Q'+str(start_qubit_id)].parse_options().pos_y,
                               flux_cpw_width='5 um',
                               flux_cpw_gap='3 um',
                               flux_cpw_width0='10 um',
                               flux_cpw_gap0='5um',
                               c_length = '15 um',
                               angle = '90',
                               # fillet = '1 um',
                               orientation='90',
                               layer='1',
                               layer_subtract='1',
                               inverse = False,
                               mirror = True,
                               subtract=True,
                               chip='main',
                             )


        control_line_list.append(MyXYLine01(design,'xy_line'+str(start_qubit_id),options=opt))
        #
        jogsS = OrderedDict()
        # jogsS[0] = ["R", str(1.25)+'mm']
        jogsS[0] = ["R", '250um']
        # jogsS[2] = ["L", '100um']

        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(0),pin='short'),
                                 end_pin=Dict(component='xy_line'+str(start_qubit_id),pin='xy_pin'),),lead = Dict(start_straight=start_straight-line_qubit_gap-line_line_gap*5,
                                 end_straight = 0.1,start_jogged_extension=jogsS,), fillet=fillet_i, chip = 'main')

        inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(start_qubit_id)+'_Q'+str(end_qubit_id)+'_'+str(0)+'_xy_line'+str(start_qubit_id),options=pin_opt))



routing_inside_pins_beta_rhs(side_pin_num=8,start_qubit_id=68,end_qubit_id=32)
routing_inside_pins_beta_rhs(side_pin_num=8,start_qubit_id=45,end_qubit_id=9)
routing_inside_pins_beta_rhs(side_pin_num=8,start_qubit_id=22,end_qubit_id=78)


# **********************************************************************************************************************************************************************************#
# wiring for remaining downside pins
# **********************************************************************************************************************************************************************************#

opt = Dict(pos_x=design.components['Q'+str(90)].parse_options().pos_x-location_x,
                       pos_y=design.components['Q'+str(90)].parse_options().pos_y,
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '-90',
                       # fillet = '1 um',
                       orientation='90',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )


control_line_list.append(MyXYLine01(design,'xy_line'+str(90),options=opt))

jogsS = OrderedDict()
jogsS[0] = ["L", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(90)+'_r',pin='short'),
                         end_pin=Dict(component='xy_line'+str(90),pin='xy_pin'),),lead = Dict(start_straight=1.5,
                         end_straight = 0.1,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(90)+'_xy_line'+str(90),options=pin_opt))

# -----------------------------------------------------------------------------------------------------------------------------

opt = Dict(pos_x=design.components['Q'+str(91)].parse_options().pos_x+location_x,
                       pos_y=design.components['Q'+str(91)].parse_options().pos_y,
                       flux_cpw_width='5 um',
                       flux_cpw_gap='3 um',
                       flux_cpw_width0='10 um',
                       flux_cpw_gap0='5um',
                       c_length = '15 um',
                       angle = '90',
                       # fillet = '1 um',
                       orientation='90',
                       layer='1',
                       layer_subtract='1',
                       inverse = False,
                       mirror = True,
                       subtract=True,
                       chip='main',
                     )


control_line_list.append(MyXYLine01(design,'xy_line'+str(91),options=opt))

jogsS = OrderedDict()
jogsS[0] = ["R", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(91),pin='short'),
                         end_pin=Dict(component='xy_line'+str(91),pin='xy_pin'),),lead = Dict(start_straight=1.5,
                         end_straight = 0.1,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

inside_pin_list.append(RoutePathfinder(design,'open_Q'+str(91)+'_xy_line'+str(91),options=pin_opt))

print('starting to render...........')



#wiring first 16 pins (both side and top)
def  get_extended_pos_y(y1,length,ydirction):  #actually it can also get x position, will correct name in future
    y_extended = y1+length*ydirction
    return y_extended
fillet = '90 um'
extended_pin_length = 0.09
extended_pin_length_end = 0.2


x_launch_zline28 =get_extended_pos_y(design.components['launch_zline028'].pins.tie.middle[0],extended_pin_length,
                                              design.components['launch_zline028'].pins.tie.normal[0])
x_launch_zline25 =get_extended_pos_y(design.components['launch_zline025'].pins.tie.middle[0],extended_pin_length,
                                              design.components['launch_zline025'].pins.tie.normal[0])
side_pin_num0 = pin_qubit_num0-pin_for_side_num
left_eps = 0.15  #length left for no collision at sides
total_wiring_space =abs(x_launch_zline25-design.components['open_Q65_Q56_8'].parse_options().pos_x)
wiring_space0 =( total_wiring_space-left_eps)/(pin_qubit_num0 )
extended_pin_length_start =wiring_space0*(side_pin_num0-1)+left_eps


side_pin_list=[]
# for i in range(3):
#     # y_launch_zline26 =get_extended_pos_y(design.components['launch_zline26'].pins.tie.middle[1],extended_pin_length,
#     #                                               design.components['launch_zline26'].pins.tie.normal[1])
#     jogsS = OrderedDict()
#     jogsS[0] = ["R", str(8-i)+"mm"]
#     pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q65_Q56_'+str(8-i),pin='short'),
#                              end_pin=Dict(component='launch_zline0'+str(26+i),pin='tie'),),lead = Dict(start_straight=total_wiring_space-i*wiring_space0,
#                              end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
#     side_pin_list.append(RoutePathfinder(design,'line_launch'+str(26+i)+'_pin0'+str(8-i),options=pin_opt))
jogsS = OrderedDict()
jogsS[0] = ["R", '100um']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q65_Q56_8',pin='short'),
                         end_pin=Dict(component='launch_zline025',pin='tie'),),lead = Dict(start_straight=total_wiring_space,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

side_pin_list.append(RoutePathfinder(design,'line_launch25'+'_pin08',options=pin_opt))


jogsS[0] = ["R", '4.6mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q65_Q56_7',pin='short'),
                         end_pin=Dict(component='launch_zline026',pin='tie'),),lead = Dict(start_straight=total_wiring_space-wiring_space0,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

side_pin_list.append(RoutePathfinder(design,'line_launch26'+'_pin07',options=pin_opt))


jogsS[0] = ["R", '4.3mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q65_Q56_6',pin='short'),
                         end_pin=Dict(component='launch_zline027',pin='tie'),),lead = Dict(start_straight=total_wiring_space-2*wiring_space0,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

side_pin_list.append(RoutePathfinder(design,'line_launch27'+'_pin06',options=pin_opt))



#wiring from side to top

side_top_pin_list = []
jogsS = OrderedDict()
jogsS[0] = ["R", '4.0mm']
jogsS[1] = ["R", 2*wiring_space0]
jogsS[2] = ["L", '100um']
jogsE = OrderedDict()
jogsE[0] = ["R", '100um']
for i in trange(side_pin_num0):
    jogsS[0] = ["R", str(4-0.3*i)+'mm']
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q65_Q56_'+str(side_pin_num0-1-i),pin='short'),
                     end_pin=Dict(component='top_virtual'+str(i),pin='short'),),lead = Dict(start_straight=total_wiring_space-(pin_for_side_num+i)*wiring_space0,
                     end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,end_jogged_extension=jogsE),
                     fillet=fillet, chip = 'main')
    side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(side_pin_num0-1-i)+'_top_vpin'+str(i),options=pin_opt))

readout_open_space = design.components['open_readout_line_l2'].parse_options().pos_y - design.components['open_Q65_Q56_0'].parse_options().pos_y
jogsS[0] = ["R", str(2.2-readout_open_space)+'mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l2',pin='short'),
                 end_pin=Dict(component='top_virtual'+str(side_pin_num0),pin='short'),),lead = Dict(start_straight=total_wiring_space-(pin_qubit_num0)*wiring_space0,
                 end_straight = (side_pin_num0+1)*extended_pin_length_end,start_jogged_extension=jogsS,end_jogged_extension=jogsE),
                 fillet=fillet, chip = 'main')

side_top_pin_list.append(RoutePathfinder(design,'readout_line_l2_top_vpin6',options=pin_opt))



#wiring first 16 pins (both side and top)----right hand side version

x_launch_zline315 =get_extended_pos_y(design.components['launch_zline315'].pins.tie.middle[0],extended_pin_length,
                                              design.components['launch_zline315'].pins.tie.normal[0])
side_pin_num0_r = pin_qubit_num0_r-pin_for_side_num

total_wiring_space_r =abs(x_launch_zline315-design.components['open_Q66_Q64_rhs7'].parse_options().pos_x)
wiring_space0_r =( total_wiring_space_r-left_eps)/(pin_qubit_num0_r)
extended_pin_length_start_r =wiring_space0_r*(side_pin_num0_r-1)+left_eps

jogsS = OrderedDict()
jogsS[0] = ["L", '100um']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q66_Q64_rhs7',pin='short'),
                         end_pin=Dict(component='launch_zline315',pin='tie'),),lead = Dict(start_straight=total_wiring_space_r,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

side_pin_list.append(RoutePathfinder(design,'line_launch315'+'_pin07',options=pin_opt))


jogsS[0] = ["L", '4.6mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q66_Q64_rhs6',pin='short'),
                         end_pin=Dict(component='launch_zline314',pin='tie'),),lead = Dict(start_straight=total_wiring_space_r-wiring_space0_r,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

side_pin_list.append(RoutePathfinder(design,'line_launch314'+'_pin06',options=pin_opt))


jogsS[0] = ["L", '4.3mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q66_Q64_rhs5',pin='short'),
                         end_pin=Dict(component='launch_zline313',pin='tie'),),lead = Dict(start_straight=total_wiring_space_r-2*wiring_space0_r,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')

side_pin_list.append(RoutePathfinder(design,'line_launch313'+'_pin05',options=pin_opt))


#wiring from side to top---right hand side version
jogsS = OrderedDict()
jogsS[0] = ["L", '4.0mm']
jogsS[1] = ["L", 2*wiring_space0_r]
jogsS[2] = ["R", '100um']
jogsE = OrderedDict()
jogsE[0] = ["L", '100um']
for i in trange(side_pin_num0_r):
    jogsS[0] = ["L", str(4-0.3*i)+'mm']
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q66_Q64_rhs'+str(side_pin_num0_r-1-i),pin='short'),
                     end_pin=Dict(component='top_virtual_r'+str(i),pin='short'),),lead = Dict(start_straight=total_wiring_space_r-(pin_for_side_num+i)*wiring_space0_r,
                     end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,end_jogged_extension=jogsE),
                     fillet=fillet, chip = 'main')
    side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(side_pin_num0_r-1-i)+'_top_vpin_r'+str(i),options=pin_opt))

readout_open_space_r = design.components['open_readout_line_r_rpin2'].parse_options().pos_y - design.components['open_Q66_Q64_0'].parse_options().pos_y
jogsS[0] = ["L", str(2.2-readout_open_space_r)+'mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_r_rpin2',pin='short'),
                 end_pin=Dict(component='top_virtual_r'+str(side_pin_num0_r),pin='short'),),lead = Dict(start_straight=total_wiring_space_r-(pin_qubit_num0_r)*wiring_space0_r,
                 end_straight = (side_pin_num0_r+1)*extended_pin_length_end,start_jogged_extension=jogsS,end_jogged_extension=jogsE),
                 fillet=fillet, chip = 'main')

side_top_pin_list.append(RoutePathfinder(design,'readout_line_r_l2_top_vpin_r'+str(side_pin_num0_r),options=pin_opt))


##--------------------------------------------------------------------------------------------------


#wiring for side pin ----part 1: enlarge pin space
pin_side_list=[]
fillet_l = '50 um'
# end_straight_step = (enlarge_xspace-0.1)*2/pin_qubit_num1
end_straight_step = 0.2
start_straight = 0.1
jogsS = OrderedDict()

def  routing_enlarge_side_pin(pin_qubit_num,top_qubit_id,low_qubit_id):
    for i in trange((pin_qubit_num)):
        if (i<int(pin_qubit_num/2)):
            pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_'+str(i),pin='short'),
                         end_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r'+str(i),pin='short'),),lead = Dict(start_straight=start_straight,
                         end_straight = enlarge_xspace-2*start_straight-i*end_straight_step,), fillet=fillet_l, chip = 'main')
            pin_side_list.append(RoutePathfinder(design,'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(i)+'_pin'+str(i),options=pin_opt))
        elif (i>int(pin_qubit_num/2)):
            pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_'+str(i),pin='short'),
                         end_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r'+str(i),pin='short'),),lead = Dict(start_straight=start_straight,
                         end_straight = enlarge_xspace-2*start_straight-(pin_qubit_num-i)*end_straight_step,), fillet=fillet_l, chip = 'main')
            pin_side_list.append(RoutePathfinder(design,'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(i)+'_pin'+str(i),options=pin_opt))
        else:
            pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_'+str(i),pin='short'),
                         end_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r'+str(i),pin='short'),), fillet=fillet_l, chip = 'main')
            pin_side_list.append(RoutePathfinder(design,'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(i)+'_pin'+str(i),options=pin_opt))





def  routing_readout_line_enlarged_pin(readout_line_id,enlarged_pin_id,top_qubit_id,low_qubit_id):
    jogsS[0] = ["R", '100um']
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l'+str(readout_line_id),pin='short'),
                 end_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(enlarged_pin_id)+'_r',pin='short'),), lead = Dict(start_straight=2*start_straight, end_straight = '100 um',start_jogged_extension=jogsS,), fillet=fillet_l, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_line_id)+'_r_pin'+str(enlarged_pin_id)+'_l',options=pin_opt))




routing_enlarge_side_pin(pin_qubit_num1,67,24)

routing_readout_line_enlarged_pin(6,0,67,24)
#

routing_enlarge_side_pin(pin_qubit_num2,42,33)

routing_readout_line_enlarged_pin(1,1,42,33)


routing_enlarge_side_pin(pin_qubit_num3,44,1)

routing_readout_line_enlarged_pin(5,2,44,1)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

##wiring for side pin ----part 1: enlarge pin space---right hand side
def  routing_enlarge_side_pin_rhs(pin_qubit_num,top_qubit_id,low_qubit_id):
    for i in trange((pin_qubit_num)):
        if (i<int(pin_qubit_num/2)):
            pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_rhs'+str(i),pin='short'),
                         end_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_l'+str(i),pin='short'),),lead = Dict(start_straight=start_straight,
                         end_straight = enlarge_xspace-2*start_straight-i*end_straight_step,), fillet=fillet_l, chip = 'main')
            pin_side_list.append(RoutePathfinder(design,'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(i)+'_pin'+str(i),options=pin_opt))
        elif (i>int(pin_qubit_num/2)):
            pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_rhs'+str(i),pin='short'),
                         end_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_l'+str(i),pin='short'),),lead = Dict(start_straight=start_straight,
                         end_straight = enlarge_xspace-2*start_straight-(pin_qubit_num-i)*end_straight_step,), fillet=fillet_l, chip = 'main')
            pin_side_list.append(RoutePathfinder(design,'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(i)+'_pin'+str(i),options=pin_opt))
        else:
            pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_rhs'+str(i),pin='short'),
                         end_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_l'+str(i),pin='short'),), fillet=fillet_l, chip = 'main')
            pin_side_list.append(RoutePathfinder(design,'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(i)+'_pin'+str(i),options=pin_opt))



def  routing_readout_line_enlarged_pin_rhs(readout_line_id,enlarged_pin_id,top_qubit_id,low_qubit_id):
    jogsS[0] = ["L", '100um']
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_r_rpin'+str(readout_line_id),pin='short'),
                 end_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(enlarged_pin_id)+'_l',pin='short'),), lead = Dict(start_straight=2*start_straight, end_straight = '100 um',start_jogged_extension=jogsS,), fillet=fillet_l, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_line_id)+'_l_pin'+str(enlarged_pin_id)+'_r',options=pin_opt))



routing_enlarge_side_pin_rhs(pin_qubit_num1_r,68,32)

routing_readout_line_enlarged_pin_rhs(6,0,68,32)


# def  routing_readout_line_enlarged_pin0_rhs(readout_line_id,enlarged_pin_id, top_qubit_id,low_qubit_id):
#     jogsS[0] = ["L", '200um']
#     pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_r_rpin'+str(readout_line_id),pin='short'),
#                  end_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(enlarged_pin_id)+'_l',pin='short'),), lead = Dict(start_straight=2*start_straight, end_straight = '100 um',start_jogged_extension=jogsS,), fillet=fillet_l, chip = 'main')
#     pin_side_list.append(RoutePathfinder(design,'readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_line_id)+'_l_pin'+str(enlarged_pin_id)+'_r',options=pin_opt))

def  routing_readout_line_enlarged_pin0_rhs(readout_line_id,enlarged_pin_id, top_qubit_id,low_qubit_id):
    jogsS: OrderedDict[str, str] = OrderedDict()
    if top_qubit_id==43:
        jogsS=OrderedDict()
    else:
        jogsS[0] = ["R", '200um']
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_r_rpin'+str(readout_line_id),pin='short'),
                 end_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(enlarged_pin_id)+'_l',pin='short'),), lead = Dict(start_straight=2*start_straight, end_straight = '100 um',start_jogged_extension=jogsS,), fillet=fillet_l, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_line_id)+'_l_pin'+str(enlarged_pin_id)+'_r',options=pin_opt))


routing_enlarge_side_pin_rhs(pin_qubit_num2_r,43,41)

routing_readout_line_enlarged_pin0_rhs(1,1,43,41)


routing_enlarge_side_pin_rhs(pin_qubit_num3_r,45,9)

routing_readout_line_enlarged_pin_rhs(5,2,45,9)


routing_enlarge_side_pin_rhs(pin_qubit_num4_r,20,18)

routing_readout_line_enlarged_pin_rhs(0,3,20,18)


routing_enlarge_side_pin_rhs(pin_qubit_num5_r,22,78)

routing_readout_line_enlarged_pin_rhs(4,4,22,78)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

#wiring for side pin ----part 1: enlarge pin space
# def  routing_readout_line_enlarged_pin0(readout_line_id,enlarged_pin_id, top_qubit_id,low_qubit_id):
#     jogsS[0] = ["R", '200um']
#     pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l'+str(readout_line_id),pin='short'),
#                  end_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(enlarged_pin_id)+'_r',pin='short'),), lead = Dict(start_straight=2*start_straight,
#                 end_straight = '100 um',start_jogged_extension=jogsS,), fillet=fillet_l, chip = 'main')
#     pin_side_list.append(RoutePathfinder(design,'readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_line_id)+'_r_pin'+str(enlarged_pin_id)+'_l',options=pin_opt))

def  routing_readout_line_enlarged_pin0(readout_line_id,enlarged_pin_id, top_qubit_id,low_qubit_id):
    jogsS: OrderedDict[str, str] = OrderedDict()
    if top_qubit_id==19:
        jogsS=OrderedDict()
    else:
        jogsS[0] = ["R", '200um']
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l'+str(readout_line_id),pin='short'),
                 end_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(enlarged_pin_id)+'_r',pin='short'),), lead = Dict(start_straight=2*start_straight,
                end_straight = '100 um',start_jogged_extension=jogsS,), fillet=fillet_l, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_line_id)+'_r_pin'+str(enlarged_pin_id)+'_l',options=pin_opt))


routing_enlarge_side_pin(pin_qubit_num4,19,10)

routing_readout_line_enlarged_pin0(0,3,19,10)


routing_enlarge_side_pin(pin_qubit_num5,21,70)

routing_readout_line_enlarged_pin(4,4,21,70)



#wiring for side pin ---- part 2: wiring enlarged pins ----

fillet = '90 um'

def routing_enlarged_pin_launchpad(pin_qubit_num, top_qubit_id,low_qubit_id,launchpad_id,launchpad_prefix,readout_line_id):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'
                        +str(readout_line_id)+'_l',pin='short'), end_pin=Dict(component='launch_zline'+str(launchpad_prefix)+str(launchpad_id),pin='tie'),),lead = Dict(start_straight=0.01,  end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'line_launch'+str(launchpad_id)+'_readout_line_pin'+str(readout_line_id),options=pin_opt))

    for i in trange(int(pin_qubit_num)):
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_l'+str(i),pin='short'),
                             end_pin=Dict(component='launch_zline'+str(launchpad_prefix)+str(int(launchpad_id-1-i)),pin='tie'),),lead = Dict(start_straight=0.01,
                             end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
        pin_side_list.append(RoutePathfinder(design,'line_launch'+str(launchpad_prefix)+str(int(launchpad_id-1-i))+'_pin'+str(i),options=pin_opt))


routing_enlarged_pin_launchpad(pin_qubit_num1,67,24,24,0,0)
routing_enlarged_pin_launchpad(pin_qubit_num2,42,33,15,0,1)

fillet_s = '40um'
extended_pin_length_s = 0.04
# #third section
# pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_Q44_Q1_pin2_l',pin='short'),
#                      end_pin=Dict(component='launch_zline0'+str(6),pin='tie'),),lead = Dict(start_straight=0.01,
#                      end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
#  pin_side_list.append(RoutePathfinder(design,'line_launch6_readout_line_Q44_Q1_pin2',options=pin_opt))
#
# for i in trange(4):
#     pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q44_Q1_l'+str(i),pin='short'),
#                          end_pin=Dict(component='launch_zline0'+str(5-i),pin='tie'),),lead = Dict(start_straight=0.01,
#                          end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
#     pin_side_list.append(RoutePathfinder(design,'line_launch0'+str(5-i)+'_pin'+str(i),options=pin_opt))
#
# # due to inadequate launchpad for one side, extend it to another side
# for i in trange(4):
#     pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q44_Q1_l'+str(4+i),pin='short'),
#                          end_pin=Dict(component='launch_zline1'+str(41-i),pin='tie'),),lead = Dict(start_straight=0.01,
#                          end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
#     pin_side_list.append(RoutePathfinder(design,'line_launch1'+str(41-i)+'_pin'+str(4+i),options=pin_opt))

#third section
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_Q44_Q1_pin2_l',pin='short'),
                     end_pin=Dict(component='launch_zline0'+str(4),pin='tie'),),lead = Dict(start_straight=0.01,
                     end_straight = extended_pin_length_s,), fillet=fillet_s, chip = 'main')
pin_side_list.append(RoutePathfinder(design,'line_launch04_readout_line_Q44_Q1_pin2',options=pin_opt))

for i in trange(4):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q44_Q1_l'+str(i),pin='short'),
                         end_pin=Dict(component='launch_zline0'+str(3-i),pin='tie'),),lead = Dict(start_straight=0.01,
                         end_straight = extended_pin_length_s,), fillet=fillet_s, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'line_launch0'+str(3-i)+'_pin'+str(i),options=pin_opt))

# due to inadequate launchpad for one side, extend it to another side
for i in trange(4):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q44_Q1_l'+str(4+i),pin='short'),
                         end_pin=Dict(component='launch_zline1'+str(41-i),pin='tie'),),lead = Dict(start_straight=0.01,
                         end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'line_launch1'+str(41-i)+'_pin'+str(4+i),options=pin_opt))

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#wiring for side pin ---- part 2: wiring enlarged pins ----right hand side


def routing_enlarged_pin_launchpad_rhs(pin_qubit_num, top_qubit_id,low_qubit_id,launchpad_id,launchpad_prefix,readout_line_id):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'
                        +str(readout_line_id)+'_r',pin='short'), end_pin=Dict(component='launch_zline'+str(launchpad_prefix)+str(launchpad_id),pin='tie'),),lead = Dict(start_straight=0.01,  end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'line_launch'+str(launchpad_id)+'_readout_line_pin'+str(readout_line_id),options=pin_opt))

    for i in trange(int(pin_qubit_num)):
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r'+str(i),pin='short'),
                             end_pin=Dict(component='launch_zline'+str(launchpad_prefix)+str(int(launchpad_id+1+i)),pin='tie'),),lead = Dict(start_straight=0.01,
                             end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
        pin_side_list.append(RoutePathfinder(design,'line_launch'+str(launchpad_prefix)+str(int(launchpad_id+1+i))+'_pin'+str(i),options=pin_opt))


routing_enlarged_pin_launchpad_rhs(pin_qubit_num1_r,68,32,16,3,0)
routing_enlarged_pin_launchpad_rhs(pin_qubit_num2_r,43,41,25,3,1)


# pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_Q45_Q9_pin2_r',pin='short'),
#                      end_pin=Dict(component='launch_zline3'+str(35),pin='tie'),),lead = Dict(start_straight=0.01,
#                      end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
#  pin_side_list.append(RoutePathfinder(design,'line_launch335_readout_line_Q45_Q9_pin2',options=pin_opt))
#
# for i in trange(4):
#     pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q45_Q9_r'+str(i),pin='short'),
#                          end_pin=Dict(component='launch_zline3'+str(36+i),pin='tie'),),lead = Dict(start_straight=0.01,
#                          end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
#     pin_side_list.append(RoutePathfinder(design,'line_launch3'+str(36+i)+'_pin'+str(i),options=pin_opt))
#
# # due to inadequate launchpad for one side, extend it to another side
# for i in trange(4):
#     pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q45_Q9_r'+str(4+i),pin='short'),
#                          end_pin=Dict(component='launch_zline2'+str(i),pin='tie'),),lead = Dict(start_straight=0.01,
#                          end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
#     pin_side_list.append(RoutePathfinder(design,'line_launch2'+str(i)+'_pin'+str(4+i),options=pin_opt))

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_Q45_Q9_pin2_r',pin='short'),
                     end_pin=Dict(component='launch_zline3'+str(37),pin='tie'),),lead = Dict(start_straight=0.01,
                     end_straight = extended_pin_length_s,), fillet=fillet_s, chip = 'main')
pin_side_list.append(RoutePathfinder(design,'line_launch337_readout_line_Q45_Q9_pin2',options=pin_opt))

for i in trange(4):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q45_Q9_r'+str(i),pin='short'),
                         end_pin=Dict(component='launch_zline3'+str(38+i),pin='tie'),),lead = Dict(start_straight=0.01,
                         end_straight = extended_pin_length_s,), fillet=fillet_s, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'line_launch3'+str(38+i)+'_pin'+str(i),options=pin_opt))

# due to inadequate launchpad for one side, extend it to another side
for i in trange(4):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q45_Q9_r'+str(4+i),pin='short'),
                         end_pin=Dict(component='launch_zline2'+str(i),pin='tie'),),lead = Dict(start_straight=0.01,
                         end_straight = extended_pin_length,), fillet=fillet, chip = 'main')
    pin_side_list.append(RoutePathfinder(design,'line_launch2'+str(i)+'_pin'+str(4+i),options=pin_opt))



spare_launchpad_num =0
starting_launchpad_id = N-pin_qubit_num3/2-spare_launchpad_num-1
routing_enlarged_pin_launchpad(pin_qubit_num4,19,10,int(starting_launchpad_id),1,3)
routing_enlarged_pin_launchpad(pin_qubit_num5,21,70,int(starting_launchpad_id-pin_qubit_num4-1),1,4)

#wiring for right hand side
starting_launchpad_id_r = pin_qubit_num3_r/2
routing_enlarged_pin_launchpad_rhs(pin_qubit_num4_r,20,18,int(starting_launchpad_id_r),2,3)
routing_enlarged_pin_launchpad_rhs(pin_qubit_num5_r,22,78,int(starting_launchpad_id_r+pin_qubit_num4_r+1),2,4)
# routing_enlarged_pin_launchpad(pin_qubit_num6,88,79,1,int(starting_launchpad_id-pin_qubit_num4-1-pin_qubit_num5-1),5)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------


#wiring for lower part of direct wiring from side to lower virtual pins

x_launch_zline18 =get_extended_pos_y(design.components['launch_zline118'].pins.tie.middle[0],extended_pin_length,
                                              design.components['launch_zline118'].pins.tie.normal[0])
side_pin_num6 = pin_qubit_num6-pin_for_side_num
left_eps = 0.15  #length left for no collision at sides

# wiring_space0 =( abs(x_launch_zline28-design.components['open_Q65_Q56_5'].parse_options().pos_x)-left_eps)/side_pin_num0
# extended_pin_length_start =wiring_space0*(side_pin_num0-1)+left_eps
total_wiring_space =abs(x_launch_zline18-design.components['open_Q88_Q79_0'].parse_options().pos_x)
wiring_space0 =( total_wiring_space-left_eps)/(pin_qubit_num6+2+2)
extended_pin_length_start =wiring_space0*(side_pin_num6-1)+left_eps

jogsS = OrderedDict()
jogsS[0] = ["L", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l3',pin='short'),
                         end_pin=Dict(component='launch_zline118',pin='tie'),),lead = Dict(start_straight=total_wiring_space,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch118'+'_readout_l3',options=pin_opt))


jogsS[0] = ["L", '4.6mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q88_Q79_0',pin='short'),
                         end_pin=Dict(component='launch_zline117',pin='tie'),),lead = Dict(start_straight=total_wiring_space-wiring_space0+0.05,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch117'+'_pin0',options=pin_opt))

jogsS[0] = ["L", '4.3mm']
# jogsS[0] = []
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q88_Q79_1',pin='short'),
                         end_pin=Dict(component='launch_zline116',pin='tie'),),lead = Dict(start_straight=total_wiring_space-2*wiring_space0,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch116'+'_pin1',options=pin_opt))

jogsS[0] = ["L", '4.0mm']
# jogsS[0] = []
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q88_Q79_2',pin='short'),
                         end_pin=Dict(component='launch_zline115',pin='tie'),),lead = Dict(start_straight=total_wiring_space-3*wiring_space0,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch115'+'_pin2',options=pin_opt))



#wiring for lower part of direct wiring from side to lower virtual pins in right hand side

x_launch_zline222 =get_extended_pos_y(design.components['launch_zline222'].pins.tie.middle[0],extended_pin_length,
                                              design.components['launch_zline222'].pins.tie.normal[0])
side_pin_num6_r = pin_qubit_num6_r-pin_for_side_num
left_eps = 0.15  #length left for no collision at sides


total_wiring_space_r =abs(x_launch_zline222-design.components['open_Q89_Q87_0'].parse_options().pos_x)
wiring_space0_r =( total_wiring_space_r-left_eps)/(pin_qubit_num6_r+2+2)
extended_pin_length_start_r =wiring_space0_r*(side_pin_num6_r-1)+left_eps


jogsS = OrderedDict()
jogsS[0] = ["R", '100um']

pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_r_rpin3',pin='short'),
                         end_pin=Dict(component='launch_zline222',pin='tie'),),lead = Dict(start_straight=total_wiring_space_r,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch222'+'_readout_r3',options=pin_opt))


jogsS[0] = ["R", '4.6mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q89_Q87_rhs0',pin='short'),
                         end_pin=Dict(component='launch_zline223',pin='tie'),),lead = Dict(start_straight=total_wiring_space_r-wiring_space0_r+0.05,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch223'+'_pin0',options=pin_opt))

jogsS[0] = ["R", '4.3mm']
# jogsS[0] = []
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q89_Q87_rhs1',pin='short'),
                         end_pin=Dict(component='launch_zline224',pin='tie'),),lead = Dict(start_straight=total_wiring_space_r-2*wiring_space0_r,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch224'+'_pin1',options=pin_opt))

jogsS[0] = ["R", '4.0mm']
# jogsS[0] = []
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q89_Q87_rhs2',pin='short'),
                         end_pin=Dict(component='launch_zline225',pin='tie'),),lead = Dict(start_straight=total_wiring_space_r-3*wiring_space0_r,
                         end_straight = extended_pin_length,start_jogged_extension=jogsS), fillet=fillet, chip = 'main')
side_pin_list.append(RoutePathfinder(design,'line_launch225'+'_pin2',options=pin_opt))


#wiring side line with low virtual pins
# design.delete_component('line_pin9_low_vpin6')
# side_pin_num0 = 6
# side_top_pin_list=[]
# left_eps = 0.15
jogsS = OrderedDict()
jogsS[0] = ["L", '3.7mm']
jogsS[1] = ["L", 2.0*wiring_space0]
jogsS[2] = ["R", '100um']
jogsE = OrderedDict()
jogsE[0] = ["L", '100um']
space_adjust = abs(design.components['open_readout_line_l7'].parse_options().pos_y-design.components['open_Q88_Q79_7'].parse_options().pos_y)
for i in trange(side_pin_num0+1):
    jogsS[0] = ["L", str(3.7-0.3*i)+'mm']
    if (i==5):
        jogsS[0] = ["L", str(3.7-0.3*i-space_adjust)+'mm']
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l7',pin='short'),
                     end_pin=Dict(component='low_virtual'+str(i),pin='short'),),lead = Dict(start_straight=total_wiring_space-(4+i)*wiring_space0,
                     end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,),
                     fillet=fillet, chip = 'main')
        side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+i)+'_low_vpin'+str(i),options=pin_opt))

    elif (i==6):
        jogsS = OrderedDict()
        jogsS[0] = ["L", '100um']
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q90',pin='short'),
                     end_pin=Dict(component='low_virtual'+str(i),pin='short'),),lead = Dict(start_straight=left_eps+0.1,
                     end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,),
                     fillet=fillet, chip = 'main')
        side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+i)+'_low_vpin'+str(i),options=pin_opt))
    else:
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q88_Q79_'+str(3+i),pin='short'),
                         end_pin=Dict(component='low_virtual'+str(i),pin='short'),),lead = Dict(start_straight=total_wiring_space-(4+i)*wiring_space0,
                         end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,),
                         fillet=fillet, chip = 'main')
        side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+i)+'_low_vpin'+str(i),options=pin_opt))

#wiring readout line with low virtual pins
fillet_l = '50um'
jogsS = OrderedDict()
jogsS[0] = ["L", '100um']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l8',pin='short'),
             end_pin=Dict(component='low_virtual'+str(7),pin='short'),),lead = Dict(start_straight=0.05,
             end_straight = (1+7)*extended_pin_length_end,start_jogged_extension=jogsS,),
             fillet=fillet_l, chip = 'main')
side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+7)+'_low_vpin'+str(7),options=pin_opt))


#wiring side line with low virtual pins ---- right hand side
side_pin_num6_r = pin_qubit_num6_r-pin_for_side_num
left_eps = 0.25+0.3  #length left for no collision at sides


total_wiring_space_r =abs(x_launch_zline222-design.components['open_Q89_Q87_0'].parse_options().pos_x)
wiring_space0_r =( total_wiring_space_r-left_eps)/(pin_qubit_num6_r+2+2)
extended_pin_length_start_r =wiring_space0_r*(side_pin_num6_r-1)+left_eps

# side_top_pin_list=[]
# x_launch_zline222 =get_extended_pos_y(design.components['launch_zline222'].pins.tie.middle[0],extended_pin_length,
#                                               design.components['launch_zline222'].pins.tie.normal[0])
# wiring_space0_r = wiring_space0_r*0.9
jogsS = OrderedDict()
# jogsS0 = OrderedDict()
jogsS[0] = ["R", '3.5mm']
jogsS[1] = ["R", 1.7*wiring_space0_r]
jogsS[2] = ["L", '100um']
jogsE = OrderedDict()
jogsE[0] = ["R", '100um']
space_adjust_r = abs(design.components['open_readout_line_r_rpin7'].parse_options().pos_y-design.components['open_Q89_Q87_8'].parse_options().pos_y)
for i in trange(side_pin_num6_r+2):
    jogsS[0] = ["R", str(3.5-0.3*i)+'mm']
    if (i==0):
        jogsS0 = OrderedDict()
        jogsS0[0] = ["R", str(3.5-0.3*i)+'mm']
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q89_Q87_rhs'+str(3),pin='short'),
                 end_pin=Dict(component='launch_zline2'+str(26),pin='tie'),),lead = Dict(start_straight=left_eps+0.1+(7-i)*wiring_space0_r,
                 end_straight = 0.1,start_jogged_extension=jogsS0,),
                 fillet=fillet, chip = 'main')
        side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3)+'_launch2'+str(26),options=pin_opt))
    elif (i==6):
        jogsS[0] = ["R", str(3.5-0.3*i-space_adjust_r-0.2)+'mm']
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_r_rpin7',pin='short'),
                     end_pin=Dict(component='low_virtual_r'+str(i-1),pin='short'),),lead = Dict(start_straight=left_eps+0.1+(7-i)*wiring_space0_r,
                     end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,),
                     fillet=fillet, chip = 'main')
        side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+i)+'_low_vpin_r'+str(i-1),options=pin_opt))

    elif (i==7):
        jogsS = OrderedDict()
        jogsS[0] = ["R", '100um']
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q91_r',pin='short'),
                     end_pin=Dict(component='low_virtual_r'+str(i-1),pin='short'),),lead = Dict(start_straight=0.15+0.1,
                     end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,),
                     fillet=fillet, chip = 'main')
        side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+i)+'_low_vpin_r'+str(i-1),options=pin_opt))
    else:
        pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_Q89_Q87_rhs'+str(3+i),pin='short'),
                         end_pin=Dict(component='low_virtual_r'+str(i-1),pin='short'),),lead = Dict(start_straight=left_eps+0.1+(7-i)*wiring_space0_r,
                         end_straight = (1+i)*extended_pin_length_end,start_jogged_extension=jogsS,),
                         fillet=fillet, chip = 'main')
        side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+i)+'_low_vpin_r'+str(i-1),options=pin_opt))



#wiring readout line with low virtual pins
fillet_l = '50um'
jogsS = OrderedDict()
jogsS[0] = ["R", str(3.5-0.3*8)+'mm']
pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_r_rpin8',pin='short'),
             end_pin=Dict(component='low_virtual_r'+str(7),pin='short'),),lead = Dict(start_straight=0.05,
             end_straight = (1+7)*extended_pin_length_end,start_jogged_extension=jogsS,),
             fillet=fillet_l, chip = 'main')
side_top_pin_list.append(RoutePathfinder(design,'line_pin'+str(3+8)+'_low_vpin_r'+str(7),options=pin_opt))



#wiring between top virtual pins and launch pad 28-41
side_top_launch_list=[]
top_pin_num = 7
# wiring for launch pad 29-34
for i in trange(side_pin_num0+top_pin_num+1):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='top_virtual_l'+str(i),pin='short'),
                             end_pin=Dict(component='launch_zline0'+str(28+i),pin='tie'),),lead = Dict(start_straight=extended_pin_length,
                            end_straight =extended_pin_length,), fillet=fillet, chip = 'main')
    side_top_launch_list.append(RoutePathfinder(design,'top_vpin_'+str(i)+'launch_zline0'+str(28+i),options=pin_opt))

#wiring for launch pad 35-41
for i in trange(top_pin_num):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='top_virtual_l'+str(i+7),pin='short'),
                             end_pin=Dict(component='launch_zline0'+str(35+i),pin='tie'),),lead = Dict(start_straight=extended_pin_length,
                            end_straight =extended_pin_length,), fillet=fillet, chip = 'main')
    side_top_launch_list.append(RoutePathfinder(design,'top_vpin_'+str(i+7)+'launch_zline0'+str(35+i),options=pin_opt))


#wiring between top virtual pins and launch pad 312-300
side_top_launch_list=[]
top_pin_num_r = 7
# wiring for launch pad 29-34
for i in trange(side_pin_num0_r+top_pin_num_r+1):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='top_virtual_l_r'+str(i),pin='short'),
                             end_pin=Dict(component='launch_zline3'+str(12-i),pin='tie'),),lead = Dict(start_straight=extended_pin_length,
                            end_straight =extended_pin_length,), fillet=fillet, chip = 'main')
    side_top_launch_list.append(RoutePathfinder(design,'top_vpin_r'+str(i)+'launch_zline3'+str(12-i),options=pin_opt))

#wiring between low virtual pins and launch pad 115-10
# side_top_launch_list=[]
low_pin_num = 7
# wiring for launch pad 29-34
for i in trange(int(side_pin_num6+low_pin_num+3)):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='low_virtual_l'+str(i),pin='short'),
                             end_pin=Dict(component='launch_zline1'+str(14-i),pin='tie'),),lead = Dict(start_straight=extended_pin_length,
                            end_straight =extended_pin_length,), fillet=fillet, chip = 'main')
    side_top_launch_list.append(RoutePathfinder(design,'low_vpin_'+str(i)+'launch_zline1'+str(14-i),options=pin_opt))



#wiring between low virtual pins and launch pad 227-241---right hand side
# side_top_launch_list=[]
low_pin_num_r = 7
# wiring for launch pad 29-34
for i in trange(int(side_pin_num6_r+low_pin_num_r+2)):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='low_virtual_l_r'+str(i),pin='short'),
                             end_pin=Dict(component='launch_zline2'+str(27+i),pin='tie'),),lead = Dict(start_straight=extended_pin_length,
                            end_straight =extended_pin_length,), fillet=fillet, chip = 'main')
    side_top_launch_list.append(RoutePathfinder(design,'low_vpin_r'+str(i)+'launch_zline2'+str(27+i),options=pin_opt))

# wiring readout line 0-9
readout_line_list = []
readout_line_num = 9
for i in trange(readout_line_num):
    pin_opt = Dict( pin_inputs=Dict(start_pin=Dict(component='open_readout_line_l_rpin'+str(i),pin='short'),
                             end_pin=Dict(component='open_readout_line_r'+str(i),pin='short'),),lead = Dict(start_straight='100um',
                            end_straight ='100um',), fillet=fillet, chip = 'main')
    readout_line_list.append(RoutePathfinder(design,'readout_line_'+str(i),options=pin_opt))

print('starting to render...........')

gui.rebuild()
gui.autoscale()

a_gds = design.renderers.gds
a_gds.options['short_segments_to_not_fillet'] = 'True'
a_gds.options['fabricate']='True'
scale_fillet = 2.0
a_gds.options['check_short_segments_by_scaling_fillet'] = scale_fillet
a_gds.options.negative_mask = {'main': [1,2]}
a_gds.options.cheese.shape = '1'
a_gds.options.cheese.delta_x = '200um'
a_gds.options.cheese.delta_y = '200um'
a_gds.options.cheese.edge_nocheese = '200 um'
a_gds.options.no_cheese.buffer = '50 um'
a_gds.options.cheese.cheese_1_radius = '25 um'
a_gds.options.cheese.view_in_file =  {'main': {1: True, 2:True},}
a_gds.options.no_cheese.view_in_file =  {'main': {1: False, 2:False}, }
a_gds.export_to_gds('100qubit_flip_chip_test_planar_JJ_v8.gds')

