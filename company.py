# Author: Johanna Schetelig & Almero Henning
# program: company.py
# date: 11/17/2021
#
# This program...

import sys
import getpass
import signal
from psycopg2 import connect
from helperfunction import *

def main():
	
	logged_in = False
	
	signal.signal(signal.SIGINT, signal_handler)
	
	# prompt for password while password is incorrect
	keepPrompting = True
	while keepPrompting: 
		print()
		dbuser = getpass.getuser()
		dbpass = getpass.getpass()

		try:
			# Open a connection to the database.
			connStr = "host=pascal.rmc.edu dbname=group5 user=%s password=%s" % (dbuser, dbpass) 
			conn = connect( connStr ) 
			
			# Create a database cursor.
			dbcursor = conn.cursor()
			
			# stop prompting if correct password was entered and no error was thrown
			keepPrompting = False
			
		# if exception is thrown
		except Exception:
			print("password incorrect, try again")
			
			# keep prompting
			prompting = True
	
	# database introduction and instructions
	print("\n--- WELCOME TO THE JOB DATABASE! ---")
	print("---         COMPANY SEGMENT        ---\n")
	
	companyIn = str(input("Enter the company name: "))
	
	command = "SELECT company_id from final.company WHERE company_name = '" + str(companyIn) + "';"
	dbcursor.execute(command)
	nameList = dbcursor.fetchall()
	
	while len(nameList) == 0 or len(nameList) > 1:
		print("\nInvalid company name\n")
		companyIn = str(input("Enter the company name: "))
	
		command = "SELECT company_id from final.company WHERE company_name = '" + str(companyIn) + "';"
		dbcursor.execute(command)
		nameList = dbcursor.fetchall()
	
	company_id = nameList[0][0]
	
	print("\nWelcome " + str(companyIn) + "!")
	print()
	
	print("This database can be used for creating or updating job listings and to create job interest reports\nOPTION 1: Create a job listing\nOPTION 2: Update a job listing\nOPTION 3: Create job interest reports")
	userInAvailable = [1,2,3]
	
	userIn = int(input("\nChoose option: "))
	
	while True:
		while userIn not in userInAvailable:
			print("\nInvalid option\n")
			userIn = int(input("Choose option: "))
		
		# Create Job Listing
		if userIn == 1:
			optionOne(dbcursor, company_id)
			
		# Update Job listing
		elif userIn == 2:
			optionTwo(dbcursor, company_id, companyIn)
		elif userIn == 3:
			optionThree(dbcursor, company_id, companyIn)
		
		print("\nThis database can be used for creating or updating job listings and to create job interest reports\nOPTION 1: Create a job listing\nOPTION 2: Update a job listing\nOPTION 3: Create job interest reports")
	
		userIn = int(input("\nChoose option: "))
	
		
# New Job Listing
def optionOne(dbcursor, company_id):
	
	job = defineJob(dbcursor, company_id)
	
	# if city not in table, add it 
	
	location_id = CheckIfInTable(dbcursor,"location_id", job["city"], "city_name", "final.location", identifier_is_string = True)
	if location_id == 0:
		command = "SELECT MAX(location.location_id) FROM final.location"
		dbcursor.execute(command)
		listApplicant = dbcursor.fetchall()
		number = listApplicant[0][0]
		newID = int(number) + 6
		command = "INSERT INTO final.location (location_id, state_name, city_name) VALUES ("+ str(newID) + ",'" + str(job["state"]) + "','" + str(job["city"]) + "');"
		dbcursor.execute(command)
		
		command = "commit;"
		dbcursor.execute(command)
		
		location_id = newID
		
	command = "SELECT MAX(jobs.job_id) FROM final.jobs"
	dbcursor.execute(command)
	jobList = dbcursor.fetchall()
	jobNumber = jobList[0][0]
	
	newJobNum = int(jobNumber) + 6
	command = "INSERT INTO final.jobs (job_id, job_title, location_id, salary, company_id, field_id, education_level) VALUES ("+ str(newJobNum) + ",'" + str(job["title"]) + "'," + str(location_id) + "," + str(job["salary"]) + "," + str(job["company"]) + "," + str(job["field"]) + "," + str(job["degree"]) + ");"
	dbcursor.execute(command)
	
	command = "commit;"
	dbcursor.execute(command)
	
	
		
# Update Job Listing
def optionTwo(dbcursor, company_id, companyIn):
	
	attributeList = []
	valueList = []
	
	# list all current jobs by this company

	command = "SELECT job_id, job_title, city_name, state_name, company_name, salary from ((final.jobs NATURAL JOIN final.location) NATURAL JOIN final.company) WHERE company_id = " + str(company_id) + ";"
	dbcursor.execute(command)
	nameList = dbcursor.fetchall()
	print("\n Current jobs: ")
	
	printJobsTable(nameList)
	
	job_id = input("Please enter the job id # of the job you would like to update: ")
	while CheckIfInTable(dbcursor, "job_id", job_id, "job_id", "final.jobs", identifier_is_string = False) == 0:
		job_id = input("Invalid job ID, please enter the job id # : ")
	
	update = input("\n Would you like to update the required degree? y/n: ")
	if update == "y":		
		degree = input("\nWhat is the job's degree required? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
		attributeList.append("education_level")
		valueList.append(str(degree))
		
	update = input("\n Would you like to update the job's field? y/n: ")
	if update == "y":
		field_input = input("Enter the field: ")
		attributeList.append("field_id")
		valueList.append(str(field_input))
		
	update = input("\n Would you like to update your job's salary? y/n: ")
	if update == "y":
		salary_input = input("Enter the minimum salary: ")
		attributeList.append("salary")
		valueList.append(str(salary_input))

	update = input("\n Would you like to update the city? y/n: ")
	if update == "y":
		city_input = input("Enter the city: ")
		state_input = input("Enter the associated state: ")
		while city_input != "" and state_input =="":
			print("\n  ---Error, Please enter a State for your previous city ---\n")
			state_input = input("Enter the associated state: ")
		location_id = fetch_location_id(dbcursor, city_input, state_input)
		attributeList.append("location_id")
		valueList.append(str(location_id))
	
	
	UpdateEntry(dbcursor, "final.jobs", attributeList, valueList, "job_id", job_id)
	#option = int(input("\nPlease enter your option (ctrl c to exit): "))

	
def optionThree(dbcursor, company_id, companyIn):
	print("\n--- JOB INTEREST REPORT for " + companyIn + " ---\n")
	
	command = "select location_id from final.jobs where company_id =  " + str(company_id) + ";"
	dbcursor.execute(command)
	locIDtemp = dbcursor.fetchall()
	loc_id = (locIDtemp[0][0])
	
	command = "select count(*) from final.applicant where location_id =  " + str(loc_id) + ";"
	dbcursor.execute(command)
	countJobtemp = dbcursor.fetchall()
	countJobInterest = (countJobtemp[0][0])

	print("Total number of prospective job seekers in your area is " + str(countJobInterest))

	
	command = "select count(company_id) from final.saved_jobs Natural join final.jobs where company_id = " + str(company_id) + ";"
	dbcursor.execute(command)
	jobCountList = dbcursor.fetchall()
	jobCount = (jobCountList[0][0])
	
	print("Total number of jobs saved for " + str(companyIn) + " is " + str(jobCount)) 
	
	command = "select distinct job_id, job_title from final.saved_jobs Natural join final.jobs where company_id = " + str(company_id) + ";"
	dbcursor.execute(command)
	jobList = dbcursor.fetchall()
	print()
	print("%-5s  %-70s %-5s" %  ("Job ID", "Job Title", "Number of Saves"))
	print("-" * 120)
	for i in range(len(jobList)):
		
		jobID = (jobList[i][0])
		jobTitle = (jobList[i][1])
		
		command = "select count(job_id) from final.saved_jobs where job_id =  " + str(jobID) + ";"
		dbcursor.execute(command)
		jobCountList = dbcursor.fetchall()
		jobCount = (jobCountList[0][0])
		
		print("%-5s   %-70s %-5s" %  (str(jobID), str(jobTitle), str(jobCount)))
	
	print("-" * 120)

def signal_handler(sig, frame):
    print('\n\n--- You exited the program. See you soon! ---\n')
    sys.exit(0)

def CheckIfInTable(dbcursor, attribute_to_select, identifier, identifier_column_name, table, identifier_is_string = True):
	if identifier_is_string:
		command = "SELECT " + attribute_to_select + " from " + table + " WHERE " + identifier_column_name  + "= '" + identifier + "';"
	else:
		command = "SELECT " + attribute_to_select + " from " + table + " WHERE " + identifier_column_name  + "= " + identifier + ";"
		
	dbcursor.execute(command)
	nameList = dbcursor.fetchall()
	
	if len(nameList) == 0 or len(nameList) > 1:
		return 0
	else:
		return nameList[0][0]
		
# @param table: name of table as string
# @param attributeList: list with all attribute names, primary key must be first attribute
# @param valueList: list with all values to fill attributes
def UpdateEntry(dbcursor, table, attributeList, valueList, primary_key_attribute, primary_key_value):
	valueIndex = 0
	for attribute in attributeList:
		command = "UPDATE " + table + " SET "+ attribute + " = " + valueList[valueIndex] + " WHERE " + primary_key_attribute +  " = " + primary_key_value + ";"
		valueIndex += 1
		dbcursor.execute(command)
	
		# save the updates
		command = "commit;"
		dbcursor.execute(command)
	print("\nAll updates have been made. ")
	
main()