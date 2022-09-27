import json
import pandas as pd
from datetime import datetime

def rest_api(input_file):
	#reading the input json_file
	with open(input_file, "r") as read_file:
		data = json.load(read_file)
	 
	#normalize for the necessary values
	frame_1_lvl = pd.json_normalize(data)
	frame_2_lvl = pd.json_normalize(frame_1_lvl["entry"])

	#begin data collection

	#output_dumps ="[\n" + "  "
	output_data_list =[]
	for jdx in range(frame_2_lvl.size):
		
		frame_3_lvl =pd.json_normalize(frame_2_lvl[jdx])

		#observationID
		if "resource.id" in frame_3_lvl:
		    observationID = frame_3_lvl["resource.id"][0]
		else:
		    observationID = "MISSING OBSERVATION ID!"
		 
		#patientID
		if "resource.subject.reference" in frame_3_lvl:
		    patientID = frame_3_lvl["resource.subject.reference"][0]
		    patientID = (patientID.split("/"))[1]
		else:
		    patientID = "MISSING PATIENT ID!"

		#performerID
		if "resource.performer" in frame_3_lvl:
		    performer_reference = frame_3_lvl["resource.performer"][0]
		    performerID = performer_reference[0]["reference"]
		    performerID = (performerID.split("/"))[1]
		else:
		    performerID = "MISSING PERFORMER ID!"
		
		#measurementCoding measurementValue measurementUnit
		measurementCoding = []
		measurementValue = []
		measurementUnit = []
		
		if "resource.component" in frame_3_lvl:
		    measurementValue_reference = frame_3_lvl["resource.component"][0]

		    for idx in measurementValue_reference:
		        if idx["code"]["coding"][0]["system"] == "http://loinc.org":
		            measurementCoding.append(idx["code"]["coding"][0])
		            
		    for idx in measurementValue_reference:
		        if "valueQuantity" in idx:
		            measurementValue.append(idx["valueQuantity"]["value"])
		            
		    for idx in measurementValue_reference:
		        if "valueQuantity" in idx:
		            measurementUnit.append(idx["valueQuantity"]["unit"])
		else:
		    if "resource.valueQuantity.value" in frame_3_lvl:
		        for idx in frame_3_lvl["resource.valueQuantity.value"]:
		            measurementValue.append(idx)
		        
		    if "resource.valueQuantity.unit" in frame_3_lvl:
		        for idx in frame_3_lvl["resource.valueQuantity.unit"]:
		            measurementUnit.append(idx)
		 
		#measurementDate
		if "resource.issued" in frame_3_lvl:
		    measurementDate = frame_3_lvl["resource.issued"][0]
		else:
		    measurementDate = "N/A"

		#dataFetched
		dataFetched = datetime.now()
		dataFetched = dataFetched.strftime("%Y-%m-%dT%H:%M:%SZ")

		#Unit corrections
		if "cm" in measurementUnit:
		    measurementUnit = ["m"]
		    measurementValue = [x/100 for x in measurementValue]

		if "g/dl" in measurementUnit:
		    measurementUnit = ["g/dL"]

		if "mg/dL" in measurementUnit:
		    measurementUnit = ["g/dL"]
		    measurementValue = [x/1000 for x in measurementValue]
	 
		if "K/µL" in measurementUnit:
		    measurementUnit = ["1/mL"]
		    
		if "10^6/µL" in measurementUnit:
		    measurementUnit = ["10^3/mL"]

		#output generation
		output_data = {"observationID": observationID,
		                "patientID": patientID,
		                "performerID": performerID,
		                "measurementCoding": measurementCoding,
		                "measurementValue": measurementValue,
		                "measurementUnit": measurementUnit,
		                "measurementDate": measurementDate,
		                "dataFetched": dataFetched}
		
		output_data_list.append(output_data)
		
	   # output_dumps += json.dumps(output_data, indent = 4)
	   # output_dumps += '\n'

	# output_dumps += "\n]"
	output_dumps = json.dumps(output_data_list, indent = 4)
		
	#write into json
	with open("output_observation.json", "w") as file:
		file.write(output_dumps)
