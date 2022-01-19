# function prompts the user for job details and creates a dictionary with the job attributes
# @param dbcursor: dbcursor
# @param company_id: company id that enters the job as an int
# returns the preferences as a dictionary ["title", "degree", "city", "state", "field", "company", "salary"]
def defineJob(dbcursor, company_id):
	job_title = input("\nPlease enter the job title for the job: ")
	degree_input = input("\nPlease enter the degree necessary for the job? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
	
	while degree_input != "0" and degree_input != "1" and degree_input != "2" and degree_input != "3" and degree_input != "4":
		degree_input = input("\nPlease enter a valid degree. (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
		
	city_input = input("Enter the city: ")	
	state_input = input("Enter the state(s): ")
	field_input = input("Enter your preferred field(s). (click enter to see options): ")
	if field_input == "":
		printFieldOptions()
		field_input = input("\nEnter your preferred field(s): ")
	salary_input = input("Enter your minimum salary. (click enter to skip): ")
	preferences = {
		"title": job_title,
		"degree": degree_input,
		"city" : city_input,
		"state": state_input,
		"field": field_input,
		"company": company_id,
		"salary": salary_input
	}
	return preferences
	
def printFieldOptions():
	print("\n\n1016 | Insurance\n1019 | Business Services\n1022 | Manufacturing\n1025 | Information Technology\n1028 | Biotech & Pharmaceuticals\n1031 | Retail\n1034 | Oil, Gas, Energy & Utilities")
	print("1037 | Government\n1040 | Health Care\n1043 | Finance\n1046 | Aerospace & Defense\n1049 | Transportation & Logistics\n1052 | Media\n1055 | Telecommunications\n1058 | Real Estate")
	print("1061 | Travel & Tourism\n1064 | Agriculture & Forestry\n1067 | Education\n1070 | Accounting & Legal\n1073 | Non-Profit\n1076 | Construction, Repair & Maintenance\n1079 | Consumer Services\n")
	  
# function prompts the user for job preferences and returns a dictionary with set preferences 
# 
def preferenceSetting(dbcursor):
	degree_input = input("\nWhat is your highest degree earned? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
	while degree_input != "0" and degree_input != "1" and degree_input != "2" and degree_input != "3" and degree_input != "4" and degree_input != "":
		degree_input = input("\nPlease enter a valid degree. (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
	city_input = input("Enter your preferred city. (click enter to skip): ")
	
	inTable = CheckIfInTable(dbcursor, "city_name", city_input, "city_name", "final.location", identifier_is_string = True)
	
	city_inputCheck = city_input.split(" ")
	
	if len(city_inputCheck) > 1:
		while (not city_inputCheck[0].isalpha() or city_inputCheck[1].isalpha() or inTable == 0) and city_input != "":
			city_input = input("This city does not have any listings, enter another city (click enter to skip city): ")
			inTable = CheckIfInTable(dbcursor,"city_name", city_input, "city_name", "final.location", identifier_is_string = True)
	else:
		
		while (not city_input.isalpha() or inTable == 0) and city_input != "":
			if city_input == "":
				break
			city_input = input("This city does not have any listings, enter another city (click enter to skip city): ")
			inTable = CheckIfInTable(dbcursor,"city_name", city_input, "city_name", "final.location", identifier_is_string = True)
			
	state_input = input("Enter your preferred state(s). (click enter to skip): ")
	while city_input != "" and state_input =="":
		print("\n  ---Error, Please enter a State for your previous city ---\n")
		state_input = input("Enter your preferred state(s). (click enter to skip): ")
	field_input = input("Enter your preferred field(s). (click enter to skip or enter 'option' to see field options)): ")
	if field_input == "option":
		printFieldOptions()
		field_input = input("Enter your preferred field(s). (click enter to skip or enter 'option' to see field options)): ")
	company_input = input("Enter your preferred company. (click enter to skip): ") 
	
	while CheckIfInTable(dbcursor,"company_name", company_input, "company_name", "final.company", identifier_is_string = True) == 0 and company_input != "":
		company_input = input("The company does not have any job listings, try again: ")
	
	if company_input != "":
		companyInID = fetch_company_id(dbcursor, str(company_input))
	else:
		companyInID = ""
	
	salary_input = input("Enter your minimum salary, in thousands. (click enter to skip): ")
	preferences = {
		"degree": degree_input,
		"city" : city_input,
		"state": state_input,
		"field": field_input,
		"company": companyInID,
		"salary": salary_input
	}
	
	return preferences

	  
def SearchJobs(dbcursor, preferences):
	command = "SELECT job_id, job_title, city_name, state_name, company_name, salary from "
	command = command + "((final.jobs NATURAL JOIN final.location) NATURAL JOIN final.company) "
	counter = 0
	
	if preferences["degree"]:	
		command = command + " WHERE education_level <= " + str(preferences["degree"])
		counter = counter + 1
		
	if preferences["city"]:	
		location_id = fetch_location_id(dbcursor, preferences["city"], preferences["state"])
		
		if counter >0:
			command = command + " and location_id = " + str(location_id)
		else:
			command = command + " WHERE location_id = " + str(location_id)
		counter = counter + 1
		
	
	if not preferences["city"] and preferences["state"]:	
		# fetch location ID state 
		command_to_fetch_location_id = "SELECT location_id from final.location WHERE state_name = '" + preferences["state"] + "';"
		dbcursor.execute(command_to_fetch_location_id)
		location_ids_list = dbcursor.fetchall()[0]
		#print(location_ids_list)
		
		possible_ids = "("
		for number in location_ids_list:
			if number != location_ids_list[-1]:
				possible_ids = possible_ids + str(number) + ","
			else:
				possible_ids = possible_ids + str(number) + ")"
		
		if counter >0:
			command = command + " and location_id in " + possible_ids
		else:
			command = command + " WHERE location_id in " + possible_ids
		counter = counter + 1
	
	if preferences["salary"]:	
		if counter >0:
			command = command + " and salary >= " + str(preferences["salary"])
		else:
			command = command + " WHERE salary >= " + str(preferences["salary"])
		counter = counter + 1
		
	if preferences["company"]:	
		if counter >0:
			command = command + " and company_id = '" + str(preferences["company"]) + "'"
		else:
			command = command + " WHERE company_id = '" + str(preferences["company"]) + "'"
		counter = counter + 1
		
	if preferences["field"]:	
		if counter >0:
			command = command + " and field_id = " + str(preferences["field"])
		else:
			command = command + " WHERE field_id = " + str(preferences["field"])
		counter = counter + 1
	
	
	command = command + ";"
		
	dbcursor.execute(command)
	jobsTable = dbcursor.fetchall()
	
	return jobsTable
	
def printJobsTable(jobsTable):
	
	if len(jobsTable) == 0:
		print("\n--- No jobs available for the specified preferences. ---")
		return False
	
	else:	
		print("\n %-5s   %-80s    %-15s   %-5s   %-30s      %3s" % ("job id", "title", "city", "state", "company", "salary"))
		print("-" * 170)
		for record in jobsTable :
			print(" %-6d   %-78s      %-17s  %-5s  %-30s      $ %3d,000" % record)
		print("-" * 170)
		return True

# fetches the location id from city name and state name
# @param city: city as string
# @param state: state abbreviation as string
def fetch_location_id(dbcursor, city, state):
	command_to_fetch_location_id = "SELECT location_id from final.location WHERE city_name = '" + city + "' and state_name = '" + state + "';"
	dbcursor.execute(command_to_fetch_location_id)
	location_id = dbcursor.fetchall()[0][0]
	return location_id
	
# fetches the company id from company name
def fetch_company_id(dbcursor, company):
	command_to_fetch_company_id = "SELECT company_id from final.company WHERE company_name = '" + str(company) + "';"
	dbcursor.execute(command_to_fetch_company_id)
	company_id = dbcursor.fetchall()[0][0]
	return company_id
	
def signal_handler(sig, frame):
    print('\n\n--- You exited the program. See you soon! ---\n')
    exit(0)
    
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
	print("\nAll updates have been made.\n ")

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