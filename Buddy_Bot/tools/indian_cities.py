import json

# Load your JSON data
with open('C:\\Users\\rs656\\Downloads\\cities.json', 'r') as file:
    data = json.load(file)

# Initialize the nested dictionary
nested_dict = {'india': {}}

# Populate the nested dictionary
for entry in data:
    state = entry['state'].lower()
    city = entry['city'].lower()
    coordinates = [entry['latitude'], entry['longitude']]
    
    if state not in nested_dict['india']:
        nested_dict['india'][state] = {}
    
    nested_dict['india'][state][city] = coordinates

# Save the nested dictionary to a new JSON file
with open('output_city.json', 'w') as file:
    json.dump(nested_dict, file, indent=4)
