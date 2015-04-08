# This Module provides routines and functions for navigating and avoiding obstacles
#
# Main function pf this module is navigate(Scan,obstacle=100.,reference_direction,segment_width=18.,segment_number=10)
# This function take a list <Scan> of environment scans from the sensor on the servo, a distance <obstacle> to decide how near
# obstacles can minimal be, a <refernce_direction> in degree to the goal, where 0 degree is traight ahead. 
# The function then returns a steering direction in
# degree between -90 and 90, such that 0 degree is centered directly straight on.
#
# The basic algorithm is adopted from these two papers:
#	http://www.academia.edu/757737/Reactive_Navigation_Algorithm_for_Wheeled_Mobile_Robots_under_Non-Holonomic_Constraints
#	http://cdn.intechopen.com/pdfs-wm/6321.pdf
#	
#
#
#
#

from __main__ import lg
import math

#constants
c_1 = .7 		#constants for cost function from paper to experiment with
c_2 = .3

#viewing angle in degree!
angle = 180.

# we assume that (because of small distances), the longitude and latitude basically are equal to normal coordinates (orthogonal)
#	=> latitude = y-coord. longitude = x-coord.
#
# GPS_data = [gpsd.fix.latitude, gpsd.fix.longitude, gpsd.fix.altitude, gpsd.fix.track, gpsd.fix.satellites, gps.fixing.time]
# GPS_destination = [latitude, longitude]

# Note: use atan2 to circumvent any trouble with atan :)

def comp_heading(GPS_from, GPS_goingto):
    "calculate heading, based on compass"
    
    # latitude = y-coord. longitude = x-coord.
    # coord = [x-coord, y-coord] in the reference frame of the car -> current_position: origin [0, 0] 
    coord = [0., 0.]
    coord[0] = GPS_goingto[1] - GPS_from[1]
    coord[1] = GPS_goingto[0] - GPS_from[0]

    phi = math.atan2(coord[1], coord[0])

    return phi*180/math.pi  #phi is angle between x-axis and direction to target, between -180 degree and 180 degree 

def comp_get_direction(GPS_destination, GPS_data):
	"returns direction to destination in degrees, between -180 and 180; means: angle between driving-direction and target."	
	
	tolerance = 10*math.pi/180 # define tolarance in angle for straight-assumption (in radiant)
	
        # phi is the angle between the car's position and the destination
	phi = comp_heading(GPS_data, GPS_destination)

	# head is the car's angle, between -180 and 180, read from gpsdData
	head = (90 - GPS_data[3])

	if head > 180:
		head = head - 360
	elif head <= -180:
		head = head + 360

	theta = head - phi
	if theta > 180: 			#test for smallest angle to target
		theta = theta - 360		# according to navigate function and sensor design: left = negative values, right = positive
	elif theta < -180:
		theta = theta + 360
	return theta 				#between -180 degree (left) and 180 degree (right)

def gap_finding(Scan, obstacle, narrow, medium, wide):	#take sensor data, obstacle distance and list for gaps
	N_free = 0											#and give back the indices for free gaps ordered as wide, medium, narrow
	for i in range(len(Scan)):
		if Scan[i] <= obstacle or i == len(Scan)-1: #obstacle:
			if N_free > 3:
				for j in range(N_free-1, -1, -1):
					wide.extend([(i-1-j)])
			elif N_free == 3:
				for j in range(N_free-1, -1, -1):
					medium.extend([(i-1-j)])
			elif N_free < 3 and N_free != 0:
				for j in range(N_free-1, -1, -1):
					narrow.extend([(i-1-j)])
			elif N_free == 0:
				pass
				#lg.prt('segment occupied!\n', inst=__name__, lv=100)
			else:
				lg.prt('error in gap finding!', inst=__name__, lv=100000)
			N_free = 0
		else:
			N_free += 1
	lg.prt("\t\t\t wide=",wide, ", medium=", medium, ", narrow=", narrow, inst=__name__, lv=150)

def cost(ref_direction, segment, segment_number, gap_width, segment_width): 
	"calculate costs for a steering direction reference_direction in degree, segment in index"
	return c_1 * abs(ref_direction - (segment - segment_number/2.)*segment_width) + c_2 * gap_width 

def minimum_cost(gap_list,ref_direction,segment_number,gap_width,segment_width): #gap:list: narrow, medium, wide!
	cost_list = [cost(ref_direction,x,segment_number,gap_width,segment_width) for x in gap_list]
	return gap_list[cost_list.index(min(cost_list))]

def calc_direction(reference_direction,narrow,medium,wide,segment_width,segment_number):		#calculate steering direction from gaps and desired direction
	#check for integer division
	index = int(round(reference_direction / segment_width) + segment_number/2.) # segment index of target direction
	if (index in wide) or (index in medium) or (index in narrow):
		return reference_direction
	else:
		if wide != []:
			return (minimum_cost(wide,reference_direction,segment_number,0,segment_width) - segment_number/2.)*segment_width	#returns an angle
		elif medium != []:
			return (minimum_cost(medium,reference_direction,segment_number,1,segment_width) - segment_number/2.)*segment_width
		elif narrow != []:
			return (minimum_cost(narrow,reference_direction,segment_number,2,segment_width) - segment_number/2.)*segment_width
		else:
			return -1 		#-1 for turn around/ go backwards.

def navigate(Scan, obstacle, reference_direction):
	#list for narrow, medium and wide gaps
	wide = []
	medium = []
	narrow = []
	scan = [x[0] for x in Scan] #from sensors you get a list [[measurement,time],[measurement,time],....]
	segment_number = len(Scan)-1
	segment_width = angle/float(segment_number)
	steer_angle = angle/5. # divide whole scanning angle into 5 parts for left, half-left, straight, half-right and right
	
	gap_finding(scan,obstacle,narrow,medium,wide)
	steering_direction = calc_direction(reference_direction,narrow,medium,wide,segment_width,segment_number)
	#returns steering direction in degree between -90 and 90, where 0 is straight
	#if steering_direction == reference_direction: #do nothing?
	if steering_direction == -1:
		return -1
	elif steering_direction < -(3*steer_angle/2.): #directons from -90 to 90 degree.
	#steer left
		desired_status = ['forward','slow','left']
	elif steering_direction < -steer_angle/2. and steering_direction >= -(3*steer_angle/2.):
	#steer half-left
		desired_status = ['forward','slow','half-left']
	elif steering_direction < steer_angle/2. and steering_direction >= -steer_angle/2.: 
	#steer straight
		desired_status = ['forward','slow','straight']
	elif steering_direction > steer_angle/2. and steering_direction <= 3*steer_angle/2.:
	#steer half right
		desired_status = ['forward', 'slow', 'half-right']
	else:
	#steer right
		desired_status = ['forward', 'slow', 'right']
	return desired_status 

#def steering_radius():
	#do something

#def get_reference_direction():
