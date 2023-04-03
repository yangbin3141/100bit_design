from qiskit_metal import draw, Dict,designs
from qiskit_metal.qlibrary.core import BaseQubit
from qiskit_metal.toolbox_metal import math_and_overrides
from qiskit_metal.qlibrary.core import QComponent
from qiskit_metal.draw import LineString
from qiskit_metal import MetalGUI, Dict, Headings
from qiskit_metal.qlibrary.core.qroute import QRouteLead, QRoutePoint, QRoute
from qiskit_metal.qlibrary.qubits.transmon_cross import TransmonCross
from qiskit_metal.qlibrary.resonator.readoutres_fc import ReadoutResFC
from  qiskit_metal.qlibrary.user_components.my_qcomponent import  New_Transomon_Cross, RouteConnector,MyReadoutRes01,MyFluxLine01,MyFluxLine02,MyConnector,MyXYLine01,MyCircle
from  qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder
from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond
import  math
from collections import  OrderedDict
import numpy as np
import time



# Initialise design
design = designs.DesignPlanar()
# Specify design name
design.metadata['design_name'] = 'FlipChip_Device'
# launch GUI
gui = MetalGUI(design)
# Allow running the same cell here multiple times to overwrite changes
design.overwrite_enabled = True

design.chips['main']['material'] = 'sapphire'
design.chips['main']['size']['size_x'] = '30 mm'
design.chips['main']['size']['size_y'] = '30mm'
design.variables.cpw_gap='5 um'
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

opt=Dict(pos_x=0 , pos_y=0, orientation='-45', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'C_chip')
opt_a=Dict(pos_x=0 , pos_y=0, orientation='45', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'C_chip')
opt_b=Dict(pos_x=0 , pos_y=0, orientation='135', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'C_chip')
opt_c=Dict(pos_x=0 , pos_y=0, orientation='-135', pad_width='245 um', pad_height='245 um', pad_gap = '100 um', lead_length = '176 um', chip = 'C_chip')
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
q0 = New_Transomon_Cross(design, 'Q0', options = Dict(pos_x=q0_x, pos_y=q0_y, layer='1'))
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

# add the readout resonators
options = Dict(
       readout_radius='50 um',
       readout_cpw_width='10 um',
       readout_cpw_gap='5 um',
       readout_cpw_turnradius='27 um',
       vertical_start_length = '40 um',
       vertical_end_length = '300 um',
       horizontal_start_length01= '400 um',
       horizontal_start_length02 = '400 um',
       horizontal_end_length = '500 um',
       total_length = '4200 um',
       arc_step='1 um',
       meander_round = '5',
       orientation='0',
       layer='2',
       layer_subtract='2',
       inverse = False,
       mirror = False,
       subtract=True,
       chip='main',)
location_x = design.components['Q0'].parse_options().cross_width/4
# the resonator is set to have its origin at the center of the circular patch.
# So we set the qubit and the resonator to share the same coordinate (q1_x, q1_y)
r0 = MyReadoutRes01(design, 'R0', options = Dict(pos_x = design.components['Q0'].parse_options().pos_x+location_x, pos_y = design.components['Q0'].parse_options().pos_y, **options))

resonator_list = []
resonator_list.append(r0)
for i in range(int(total_qubit_num)-1):
     location = design.components['Q'+str(i+1)] .parse_options().cross_width/4
     resonator_list.append(design.copy_qcomponent(r0,'R'+str(i+1), Dict(pos_x =design.components['Q'+str(i+1)].parse_options().pos_x+location,pos_y=design.components['Q'+str(i+1)].parse_options().pos_y)))

rr_space = 0.025
design.components['R0'].options.mirror = True
design.components['R0'].options.inverse = True
design.components['R0'].options.meander_round = '3'

r_0 = design.components['R0'].parse_options().readout_radius
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
        otg = OpenToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_'+str(i),
                options=Dict(pos_x=pos_start_x,  pos_y=pos_start_y-i*pin_pin_space, orientation='0'))
        otg1 = OpenToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_rhs'+str(i),
        options=Dict(pos_x=pos_start_x,  pos_y=pos_start_y-i*pin_pin_space, orientation='180'))
        pin_qubit_list.append(otg)
        pin_qubit_list.append(otg1)
    return pos_start_y,pos_end_y,pin_pin_space

def set_enlarged_side_pins(pos_start_y, pin_qubit_num,pin_pin_space,pin_pin_space_l,pos_start_x_l, top_qubit_id,low_qubit_id):
    pos_start_y_l = pos_start_y-int((pin_qubit_num)/2)*pin_pin_space+int((pin_qubit_num)/2)*pin_pin_space_l
    # pos_end_y_l = pos_end_y-(pin_qubit_num-1)*pin_pin_space_l
    for i in range(pin_qubit_num):
        otg = OpenToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r'+str(i),
                                            options=Dict(pos_x=pos_start_x_l,  pos_y=pos_start_y_l-i*pin_pin_space_l, orientation='180'))
        pin_qubit_list.append(otg)
    for i in range(pin_qubit_num):
        otg = OpenToGround(design, 'open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_l'+str(i),
                           options=Dict(pos_x=pos_start_x_l,  pos_y=pos_start_y_l-i*pin_pin_space_l, orientation='0'))
        pin_qubit_list.append(otg)


def  set_enlarged_readout_line_pins(pos_start_x_l, pin_pin_space_l, top_qubit_id,low_qubit_id,readout_id): # for qubit_num=8
    pin_qubit_list.append(OpenToGround(design, 'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_r', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r0'].parse_options().pos_y+pin_pin_space_l, orientation='180')))
    pin_qubit_list.append(OpenToGround(design,  'open_readout_line_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_pin'+str(readout_id)+'_l', options=Dict(pos_x=pos_start_x_l,  pos_y=design.components['open_Q'+str(top_qubit_id)+'_Q'+str(low_qubit_id)+'_r0'].parse_options().pos_y+pin_pin_space_l, orientation='0')))



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
set_enlarged_readout_line_pins(pos_start_x_l_r,pin_pin_space_l_r, 43,41,1)

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
set_enlarged_readout_line_pins(pos_start_x_l,pin_pin_space_l,19,10,3)

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

pin_qubit_list.append(OpenToGround(design, 'open_Q90', options=Dict(pos_x=pos_start_x,  pos_y=design.components['Q90'].parse_options().pos_y-pin_start_space, orientation='0')))
pin_qubit_list.append(OpenToGround(design, 'open_Q90_r', options=Dict(pos_x=pos_start_x,  pos_y=design.components['Q90'].parse_options().pos_y-pin_start_space, orientation='180')))

pos_start_y_r,pos_end_y_r,pin_pin_space_r = set_side_pins(pos_start_x_r,pin_qubit_num6_r,89,87)

pin_qubit_list.append(OpenToGround(design, 'open_Q91', options=Dict(pos_x=pos_start_x_r,  pos_y=design.components['Q91'].parse_options().pos_y-pin_start_space, orientation='0')))
pin_qubit_list.append(OpenToGround(design, 'open_Q91_r', options=Dict(pos_x=pos_start_x_r,  pos_y=design.components['Q91'].parse_options().pos_y-pin_start_space, orientation='180')))


#set the read line pins
readline_pos_y_list =[]
for i in [0,23,46,69]:
    readline_pos_y_list.append(design.components['R'+str(i)].pins.readout.middle[1]+(design.components['R'+str(i+5)].pins.readout.middle[1]-design.components['R'+str(i)].pins.readout.middle[1])/2)
for i in [21,44,67,90]:
    readline_pos_y_list.append(design.components['R'+str(i)].pins.readout.middle[1]+(design.components['R'+str(i-9)].pins.readout.middle[1]-design.components['R'+str(i)].pins.readout.middle[1])/2)
readline_pos_y_list.append(design.components['R92'].pins.readout.middle[1]+rr_space)

for i in range(len(readline_pos_y_list)):
    otg0 = OpenToGround(design, 'open_readout_line_l'+str(i), options=Dict(pos_x=pos_start_x,  pos_y=readline_pos_y_list[i], orientation='0'))
    otg0_r = OpenToGround(design, 'open_readout_line_l_rpin'+str(i), options=Dict(pos_x=pos_start_x,  pos_y=readline_pos_y_list[i], orientation='180'))
    otg1 = OpenToGround(design, 'open_readout_line_r'+str(i), options=Dict(pos_x=-pos_start_x,  pos_y=readline_pos_y_list[i], orientation='0'))
    otg1_r = OpenToGround(design, 'open_readout_line_r_rpin'+str(i), options=Dict(pos_x=-pos_start_x,  pos_y=readline_pos_y_list[i], orientation='180'))
    pin_qubit_list.append(otg0)
    pin_qubit_list.append(otg1)

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
    stg = OpenToGround(design, 'top_virtual'+str(i), options=Dict(pos_x=top_vpin_start_pos_x+i*top_vpin_space,  pos_y=top_vpin_pos_y, orientation='90'))
    stg1 = OpenToGround(design, 'top_virtual_r'+str(i), options=Dict(pos_x=-(top_vpin_start_pos_x+i*top_vpin_space),  pos_y=top_vpin_pos_y, orientation='90'))
    top_vpin_list.append(stg)
    top_vpin_list.append(stg1)
    stg2 = OpenToGround(design, 'top_virtual_l'+str(i), options=Dict(pos_x=top_vpin_start_pos_x+i*top_vpin_space,  pos_y=top_vpin_pos_y, orientation='-90'))
    stg3 = OpenToGround(design, 'top_virtual_l_r'+str(i), options=Dict(pos_x=-(top_vpin_start_pos_x+i*top_vpin_space),  pos_y=top_vpin_pos_y, orientation='-90'))
    top_vpin_launch_list.append(stg2)
    top_vpin_launch_list.append(stg3)


# for i in range(top_vpin_num):
#     stg = OpenToGround(design, 'top_virtual_l'+str(i), options=Dict(pos_x=top_vpin_start_pos_x+i*top_vpin_space,  pos_y=top_vpin_pos_y, orientation='-90'))
#     top_vpin_launch_list.append(stg)
low_vpin_num = top_vpin_num+2
low_vpin_pos_y = design.components['launch_zline113'].parse_options().pos_y+pad_pin_vspace-0.5
low_vpin_start_pos_x = design.components['Q92'].parse_options().pos_x
low_vpin_end_pos_x = design.components['Q96'].parse_options().pos_x-0.1
low_vpin_space =abs( low_vpin_end_pos_x-low_vpin_start_pos_x)/(low_vpin_num-1)
for i in range(low_vpin_num):
    stg = OpenToGround(design, 'low_virtual'+str(i), options=Dict(pos_x=low_vpin_start_pos_x+i*low_vpin_space,  pos_y=low_vpin_pos_y, orientation='-90'))
    stg1 = OpenToGround(design, 'low_virtual_r'+str(i), options=Dict(pos_x=-(low_vpin_start_pos_x+i*low_vpin_space),  pos_y=low_vpin_pos_y, orientation='-90'))
    top_vpin_list.append(stg)
    top_vpin_list.append(stg1)
    stg2 = OpenToGround(design, 'low_virtual_l'+str(i), options=Dict(pos_x=low_vpin_start_pos_x+i*low_vpin_space,  pos_y=low_vpin_pos_y, orientation='90'))
    stg3 = OpenToGround(design, 'low_virtual_l_r'+str(i), options=Dict(pos_x=-(low_vpin_start_pos_x+i*low_vpin_space),  pos_y=low_vpin_pos_y, orientation='90'))
    top_vpin_launch_list.append(stg2)
    top_vpin_launch_list.append(stg3)

gui.rebuild()
gui.autoscale()