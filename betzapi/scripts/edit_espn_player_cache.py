import json


def main():
    
    FILE = 'betzapi/cache/espn_players.json'

    # Load the file
    with open(FILE, 'r') as file:
        json_file = json.load(file)
    
    # Modify the JSON: Add a new field to each player
    for player, details in json_file.items():
        url = details['splits'].replace('splits', 'gamelog')
        details['gamelog'] = url

    # Save the modified JSON back to the file
    with open(FILE, 'w') as file:
        json.dump(json_file, file, indent=4)

    print("JSON file updated successfully!")
            
            
if __name__ == '__main__':
    main()