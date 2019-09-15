from configparser import ConfigParser

def get_database_configuration(filename='database.ini', section ='postgresql'):
	parser = ConfigParser()
	parser.read(filename)

	database = {}
	if parser.has_section(section):
		parameterss = parser.items(section)
		for param in parameterss:
			database[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))

	return database