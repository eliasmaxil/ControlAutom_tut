# Import
from apm import *
	
# Select server
server = 'http://byu.apmonitor.com'

app = 'reactor'

# Clear previous application
apm(server,app,'clear all')

# Load model file
apm_load(server,app,'cstr.apm')

# Load time points for future predictions
csv_load(server,app,'cstr.csv')

# Load replay replay data for local use
#data = csv.reader(open('doublet.csv', 'rb'))
data = csv.reader(open('control.csv', 'rb'))
#data = csv.reader(open('replay1.csv', 'rb'))
#data = csv.reader(open('replay2.csv', 'rb'))
#data = csv.reader(open('replay3.csv', 'rb'))
replay = []
for row in data:
	replay.append(row)
len_replay = len(replay)

# APM Variable Classification
# class = FV, MV, SV, CV
#   F or FV = Fixed value - parameter may change to a new value every cycle
#   M or MV = Manipulated variable - independent variable over time horizon
#   S or SV = State variable - model variable for viewing
#   C or CV = Controlled variable - model variable for control

#Parameters
FVs = 'Cooling_Temp','Flow','Feed_Conc','Feed_Temp'
#FVs = 'v','rho','cp','mdelh','eoverr','k0','ua'
MVs = '---'

#Variables
SVs = 'Concentration','---'
CVs = 'Temperature','---'

# Set up variable classifications for data flow
for x in FVs: apm_info(server,app,'FV',x)
for x in MVs: apm_info(server,app,'MV',x)
for x in SVs: apm_info(server,app,'SV',x)
for x in CVs: apm_info(server,app,'CV',x)

# Options

# controller mode (1=simulate, 2=predict, 3=control)
#apm_option(server,app,'nlc.reqctrlmode',3)

# time units (1=sec,2=min,3=hrs,etc)
apm_option(server,app,'nlc.ctrl_units',2)
apm_option(server,app,'nlc.hist_units',2)

# set controlled variable error model type
apm_option(server,app,'nlc.cv_type',1)
apm_option(server,app,'nlc.ev_type',1)
apm_option(server,app,'nlc.reqctrlmode',1)

# read discretization from CSV file
apm_option(server,app,'nlc.csv_read',1)

# turn on historization to see past results
apm_option(server,app,'nlc.hist_hor',100)

# set web plot update frequency
apm_option(server,app,'nlc.web_plot_freq',3)

# set web plot update frequency
apm_option(server,app,'nlc.nodes',6)

# Objective for Nonlinear Control

# Manipulated variables (u)
apm_option(server,app,'cooling_temp.upper',350)
apm_option(server,app,'cooling_temp.lower',250)
apm_option(server,app,'flow.upper',150)
apm_option(server,app,'flow.lower',50)
apm_option(server,app,'feed_conc.upper',1.0)
apm_option(server,app,'feed_conc.lower',0.5)
apm_option(server,app,'feed_temp.upper',400)
apm_option(server,app,'feed_temp.lower',300)

# imode (1=ss, 2=mpu, 3=rto, 4=sim, 5=mhe, 6=nlc)
apm_option(server,app,'nlc.imode',1)
solver_output = apm(server,app,'solve')
apm_option(server,app,'nlc.imode',4)

for isim in range(1, len_replay-1):
	print ('')
	print ('--- Cycle %i of %i ---' %(isim,len_replay))

	# allow server to process other requests
	time.sleep(0.5)

	for x in FVs:
		value = csv_element(x,isim,replay)
		if (not math.isnan(value)):
			response = apm_meas(server,app,x,value)
			print response
	for x in MVs:
		value = csv_element(x,isim,replay)
		if (not math.isnan(value)):
			response = apm_meas(server,app,x,value)
			print response
	for x in CVs:
		value = csv_element(x,isim,replay)
		if (not math.isnan(value)):
			response = apm_meas(server,app,x,value)
			print response

	# schedule a set point change at cycle 40
	#if (isim==4): apm_option(server,app,'volume.sp',50)

	# Run NLC on APM server
	solver_output = apm(server,app,'solve')
	print (solver_output)

	if (isim==1):
		# Open Web Viewer and Display Link
		print "Opening web viewer"
		url = apm_web(server,app)

	# Retrieve results (MEAS,MODEL,NEWVAL)
	# MEAS = FV, MV,or CV measured values
	# MODEL = SV & CV predicted values
	# NEWVAL = FV & MV optimized values
