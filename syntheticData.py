from datetime import timedelta, date
import numpy, argparse, csv

#define next state at time *time* (never actually used?)
def nextState(currentSt, time, tr):
	#print('!!!Time: ', time)
	#states: Home, Work, Away
	states=[]
	#transition probabilities from currentSt to every other state
	pr=[]
	#take the states and their respective probabilities from the dictionary tr
	for x in tr.keys():
		# print(x)
		#print(tr[x][time])
		states.append(x)
		pr.append(tr[x][time])
	return states, pr


#calculate the drive time
def driveTime(timeTaken):
	alpha=numpy.random.uniform()
	driveTime=alpha*timeTaken
	return driveTime


#charge EV everytime home (10mins at time)
def recharge(sob, batteryCapacity, elapsedTime):
	#print("RECHARGING")
	#0.75=amonut of energy the household provides the EV for charging
	energyOutput=energyCapacity*0.75
	increment=energyOutput*(elapsedTime/60)
	if sob+increment>batteryCapacity:
		return batteryCapacity-sob, energyOutput
	return increment, energyOutput


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


parser=argparse.ArgumentParser(description='Enter the number of days you want to produce data for.')
#parser.add_argument('--days', metavar='N', type=int, help='an integer for the number of days')
parser.add_argument('--users', metavar='M', type=int, help='user number')

#interval for monitoring states
elapsedTime=15
#energy capacity for a household
energyCapacity=7
#possible km to drive to go to work
driveKm=[5,10,15,20,25,30,35,40,45,50]
#EV battery size (kWh)
batterySize=[25, 35, 50, 100]
#full starting battery of the EV + battery capacity (percentage)
sob=100

args=parser.parse_args()

#days=args.days
userNo=args.users
if __name__ == "__main__":

	for num in range(userNo):
		print('User: ', num)
		#user uses always the same car (same capacity)
		batteryCapacity=numpy.random.choice(batterySize)
		with open('Data/user' + str(num) + '.csv', 'w') as csvfile:
			writer = csv.writer(csvfile, delimiter=',')
			writer.writerow(['Day', 'Hour', 'State', 'Trip distance (km)', 'State Of Battery (kW)', 'Socket output (kWh)'])
			with open('finalTransitions.csv', 'rU') as inputfile:
				reader=csv.reader(inputfile, delimiter=',')
				start_date = date(2017, 1, 1)
				end_date = date(2018, 1, 1)
				#transition probability 'matrix'(0<tr<=1);
				tr={}
				tr['home']=[]
				tr['work']=[]
				tr['away']=[]
				for row in reader:
					#print(row)
					for x in row:
						#print(x)
						if row[0]=='Home' and x!='Home':
							tr['home'].append(round((float(x)/100), 3))
						elif row[0]=='Work' and x!='Work':
							tr['work'].append(round((float(x)/100), 3))
						elif row[0]=='Away' and x!='Away':
							tr['away'].append(round((float(x)/100), 3))
				#1-1-17 starts at home for every user
				currentSt='home'
				for single_date in daterange(start_date, end_date):
					takeTrip=False
					#every activity is done for at least 10 minutes
					timeTaken=0
					x=0
					#the distance of the trip to/from work is re-calculated every day
					homeWorkTrip=numpy.random.choice(driveKm)
					skipNext=True
					while x<1440: #minutes in a day
						hour=int(x/60)
						if not skipNext:
							states,pr=nextState(currentSt, hour, tr)
							# print('states: ', states)
							# print('pr: ', pr)
							#choose random state with associated probability
							nextSt=numpy.random.choice(states, p=pr)
							skipNext=True
						elif skipNext:
							nextSt=currentSt
							skipNext=False
						#increment or reset time for the activity
						if nextSt==currentSt:
							timeTaken+=elapsedTime
						else:
							timeTaken=elapsedTime
							takeTrip=True
						#print("Here I am! Current state: ", currentSt)
						tripDistance=0
						if (takeTrip):
							#car trip cannot last less than 10 minutes
							tripTime=int(driveTime(timeTaken)+10)
							#travel always the same distance to/from work
							if currentSt=='home' and nextSt=='work' or currentSt=='work' and nextSt=='home':
								tripDistance=homeWorkTrip
							else:
								#if traveling away (not home/work), re-calculate trip length
								tripDistance=numpy.random.choice(driveKm)
							takeTrip=False
							#print('Taking trip! Long: ', tripDistance)
							#print(tripTime)
							#kW consumed during this trip
							#3.25km/kWh buck–boost and UCAP system is connected [ref: https://pdfs.semanticscholar.org/c126/fe6c20661840dfb6cf4ab9c762dcf6fe4668.pdf]
							energyConsumed=tripDistance/3.25
							#print('energyConsumed: ', energyConsumed)
							#percentageConsumed=(energyConsumed/batteryCapacity)*100
							#prevent negative battery (stay elapsedTime mins more in the same state instead of changing)
							if sob-energyConsumed<0 and nextSt!='home':
								#percentageConsumed=0
								energyConsumed=0
								nextSt='home'
								tripDistance=0
							#state of battery after this trip (remaining percentage)
							sob-=round(energyConsumed, 2)
						#print("State of Battery: ", sob)
						currentSt=nextSt
						timeHour=int(x/60)
						timeMinute=int(x%60)
						#print(timeHour, timeMinute, currentSt)
						energyOutput=0
						if currentSt=='home':
							energyIncrement,energyOutput=recharge(sob, batteryCapacity, elapsedTime)
							sob+=energyIncrement
						x+=elapsedTime
						#print(str(dayToPrint)+'.'+str(month), str(timeHour)+':'+str(timeMinute), str(currentSt), str(sob), str(energyOutput))
						#dump data on csv with the format: day-hour-consumption
						writer.writerow([single_date.strftime("%Y-%m-%d"), str(timeHour)+':'+str(timeMinute), str(currentSt), str(tripDistance), str(sob), str(energyOutput)])





"""
IF AWAY AND BATTERY IS OVER, I DIRECTLY GO HOME WITHOUT CONSUMING ENERGY
"""