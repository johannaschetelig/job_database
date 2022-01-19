# Author: Johanna Schetelig & Almero Henning
# program: final.py
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

			keepPrompting = False
			
		# if exception is thrown keep prompting
		except Exception:
			print("password incorrect, try again")
			prompting = True
	
	# database introduction and instructions
	print("\n--- WELCOME TO THE JOB DATABASE! ---")
	print("---      APPLICANT SEGMENT       ---\n")
	print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
	
	option = (input("\nPlease enter your option (ctrl-c to exit): "))
	if option != "":
		option = int(option)
	else:
		option = int(input("\nPlease enter your option (ctrl-c to exit): "))
	
	while True:
		
		# create new profile
		if option == 1:
			full_name = input("\nPlease enter your full name: ")
			
			nameParts = full_name.split(" ")
			
			nameNotOK = False
			
			for i in range(len(nameParts)):
					if not nameParts[i].isalpha():
						nameNotOK = True
			
			while nameNotOK:
				nameNotOK = False
				print("Invalid entry")
				full_name = input("\nPlease enter your full name (only letters): ")
				nameParts = full_name.split(" ")
				
				for i in range(len(nameParts)):
					if not nameParts[i].isalpha():
						nameNotOK = True

			preferences = preferenceSetting(dbcursor)
						
			# look up largest userId and create new userid
			command = "SELECT MAX(applicant.applicant_id) FROM final.applicant"
			dbcursor.execute(command)
			listApplicant = dbcursor.fetchall()
			number = listApplicant[0][0]
			
			# first applicant
			if number == None:
				number = 0
			new_id = number+1
			user_id = new_id
			logged_in = True
			current_user = new_id
			
			# add new applicant to table (name, id, preferences)
			command = "INSERT INTO final.applicant (applicant_name, applicant_id"
			entry = "'" + full_name + "'," + str(new_id) 
			if preferences["city"] != "":
				location_id = fetch_location_id(dbcursor, preferences["city"], preferences["state"])
				command = command + ",location_id"
				entry = entry + "," + str(location_id)
			if preferences["salary"] != "":
				command = command + ",salary"
				entry = entry + "," + str(preferences["salary"])
			if preferences["field"] != "":
				command = command + ",field_id"
				entry = entry + ","+ str(preferences["field"])
			if preferences["company"] != "":
				
				
				command = command + ",company_id"
				entry = entry + ","+ str(preferences["company"]) 
			if preferences["degree"] != "":
				command = command + ",education_level"
				entry = entry + ","+ str(preferences["degree"])
		
			command = command + ") VALUES (" + entry +");"
			dbcursor.execute(command)
			
			# save the updates
			command = "commit;"
			dbcursor.execute(command)
			string = "\nHello " + full_name + ", your user-id is " + str(new_id) + ". Please save this for future reference. "
			print(string)
			
			print("-"*40)
			print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
			option = int(input("\nPlease enter your option (ctrl-c to exit):"))
		
		# log in 
		elif option == 2:
			
			user_id = input("\nEnter your user id: ")
			
			while CheckIfInTable(dbcursor,"applicant_id", user_id, "applicant_id", "final.applicant", identifier_is_string = True) == 0:
				user_id = input("The id entered does not match an existing user, try again: ")
			
			# search for user_id and check if valid
			command = "SELECT applicant_name from final.applicant WHERE applicant_id =" + user_id +";"
			dbcursor.execute(command)
			list = dbcursor.fetchall()
			applicant_name = list[0][0]
			print("\nHello ", applicant_name.strip() , "! You have successfully logged in.\n", sep="")
			logged_in = True
			
			command = "SELECT education_level, location_id, field_id, company_id, salary from final.applicant WHERE applicant_id =" + user_id +";"
			dbcursor.execute(command)
			preference_list = dbcursor.fetchall()
			
			degree = preference_list[0][0]
			location_id = preference_list[0][1]
			
			if location_id:
				command = "SELECT state_name, city_name from final.location WHERE location_id =" + str(location_id) +";"
				dbcursor.execute(command)
				location_id_list = dbcursor.fetchall()
				state = location_id_list[0][0]
				city = location_id_list[0][1]
			else:
				state = None
				city = None
				
			field = preference_list[0][2]
			company = preference_list[0][3]
			salary = preference_list[0][4]
			
			preferences = {
				"degree": degree,
				"city" : city,
				"state": state,
				"field": field,
				"company": company,
				"salary": salary
				}
			
			print("-"*40)
			print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
			option = int(input("\nPlease enter your option (ctrl-c to exit): "))
			
		# search database
		elif option ==3:
			if not logged_in:
				continue_to_login = input("You are currently logged in as a guest user, would you like to log in? y/n: ")
				if continue_to_login == "y":
					print("switching to login")
					option = 2
				else:
					print("\n you will continue as a guest user. \n")
			
					preferences = preferenceSetting(dbcursor)
					jobsTable = SearchJobs(dbcursor, preferences)
					printJobsTable(jobsTable)
					
					print("-"*40)
					print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
					option = int(input("\nPlease enter your option (ctrl-c to exit): "))
			else:
				jobsTable = SearchJobs(dbcursor, preferences)
				if printJobsTable(jobsTable):
					
				
					save_input = input("\nWould you like to save any of these jobs? y/n: ")
					
					if save_input == "y":
						job_ids = input("Please enter the job id numbers you want to save (comma-separated): ")
						job_list = job_ids.split(",")
						for job in job_list:
							command = "INSERT INTO final.saved_jobs (job_id, applicant_id) VALUES ("+ job + "," + str(user_id) + ");"
							dbcursor.execute(command)
							# save the updates
							command = "commit;"
							dbcursor.execute(command)
				
				print()
				print("-"*40)
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = int(input("\nPlease enter your option (ctrl-c to exit): "))
				
		# Show saved jobs
		elif option ==4:
			if not logged_in:
				option = 2
			else:
				command = "CREATE TEMP TABLE saved_jobs as SELECT job_id from final.saved_jobs WHERE applicant_id = " + str(user_id) + ";"
				dbcursor.execute(command)
				command = "commit;"
				dbcursor.execute(command)
				command = "SELECT job_id, job_title, city_name, state_name, company_name, salary from (((final.jobs NATURAL JOIN final.saved_jobs)  NATURAL JOIN final.location) NATURAL JOIN final.company) where applicant_id = " + str(user_id) + ";"
				dbcursor.execute(command)
				job_list = dbcursor.fetchall()
				
				print("\n %-5s   %-80s    %-15s   %-5s   %-30s      %3s" % ("job #", "title", "city", "state", "company", "salary"))
				print("-" * 170)
				for record in job_list :
					print(" %-6d   %-78s      %-17s  %-5s  %-30s      $ %3d,000" % record)
				print("-" * 170)

				print()			
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = int(input("\nPlease enter your option (ctrl-c to exit): "))
			
		# change preferences
		elif option ==5:
			if not logged_in:
				option = 2
			else:
				attributeList = []
				valueList = []
				
				update = input("\n Would you like to update your degree? y/n: ")
				if update == "y":		
					degree = input("\nWhat is your highest degree earned? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
					if degree != "":
						attributeList.append("education_level")
						valueList.append(str(degree))
					else:
						command = "UPDATE " + "final.applicant" + " SET "+ "education_level" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
					
				update = input("\n Would you like to update your field? y/n (enter 'option' to see field options): ")
				if update == "option":				
					print("\n\n1016 | Insurance\n1019 | Business Services\n1022 | Manufacturing\n1025 | Information Technology\n1028 | Biotech & Pharmaceuticals\n1031 | Retail\n1034 | Oil, Gas, Energy & Utilities")
					print("1037 | Government\n\n1040 | Health Care\n1043 | Finance\n1046 | Aerospace & Defense\n1049 | Transportation & Logistics\n1052 | Media\n1055 | Telecommunications\n1058 | Real Estate")
					print("1061 | Travel & Tourism\n1064 | Agriculture & Forestry\n1067 | Education\n1070 | Accounting & Legal\n1073 | Non-Profit\n1076 | Construction, Repair & Maintenance\n1079 | Consumer Services\n")
				if update == "y":	
					field_input = input("Enter your preferred field: ")
					if field_input != "":
						attributeList.append("field_id")
						valueList.append(str(field_input))
					else:
						command = "UPDATE " + "final.applicant" + " SET "+ "field_id" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
				
				update = input("\n Would you like to update your company? y/n: ")
				if update == "y":	
					company_input = input("Enter your preferred company: ")
					if company_input != "":
						attributeList.append("company_id")
						valueList.append(str(company_input))
					else:
						command = "UPDATE " + "final.applicant" + " SET "+ "company_id" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
					
				update = input("\n Would you like to update your salary? y/n: ")
				if update == "y":
					salary_input = input("Enter your minimum salary: ")
					if salary_input != "":
						attributeList.append("salary")
						valueList.append(str(salary_input))
					else:
						command = "UPDATE " + "final.applicant" + " SET "+ "salary" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")

				update = input("\n Would you like to update your city? y/n: ")
				if update == "y":
					
					state_input = ""
					
					city_input = input("Enter your preferred city: ")
					if city_input != "":
						state_input = input("Enter the associated state: ")
					while city_input != "" and state_input =="":
						print("\n  ---Error, Please enter a State for your previous city ---\n")
						state_input = input("Enter the associated state: ")
					
					if city_input != "":
						location_id = fetch_location_id(dbcursor, city_input, state_input)
						attributeList.append("location_id")
						valueList.append(str(location_id))
					else:
						command = "UPDATE " + "final.applicant" + " SET "+ "location_id" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
				else:
					update = input("\n Would you like to update your state? y/n: ")
					if update == "y":
						state_input = input("Enter your preferred state: ")
						city_input = None
						if state_input != "":
							location_id = fetch_location_id(dbcursor, city_input, state_input)
							attributeList.append("location_id")
							valueList.append(str(location_id))
				
				
				UpdateEntry(dbcursor, "final.applicant", attributeList, valueList, "applicant_id", str(user_id))
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = int(input("\nPlease enter your option (ctrl c to exit): "))
			
		else:
			
			print("Invalid input, try again.")
			print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
			option = (input("\nPlease enter your option (ctrl c to exit): "))
			
			while not option.isnumeric():
				print("Invalid input, try again.")
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = (input("\nPlease enter your option (ctrl c to exit): "))

			option = int(option)
		
main()