# Pseudocode zur Strukturierung

drive.py

drive.steer(current_status, desired_status)         # status = [direction,velocity,steer position]
drive.accelerate(current_status, desired_status)
drive.print_status(status)
drive.driving(current_status, desired_status)       # first accelerate, then steer
drive.right90(current_status, desired_status, speed='middle')
drive.left90(current_status, desired_status, speed='middle')
drive.turn180(current_status, desired_status, speed='middle')



gpsData.py      # Max: made edit which should output important data. Not sure though.
