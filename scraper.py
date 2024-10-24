
import requests
from jinja2 import Template
from datetime import timedelta

# Read team numbers from the file
with open('teams.txt', 'r') as f:
    team_numbers = [line.strip() for line in f.readlines()]

# Define the base API URL
base_url = "https://scoreboard.uscyberpatriot.org/api/image/scores.php?team%5B%5D="

# Function to fetch data for a team
def fetch_team_data(team_number):
    response = requests.get(base_url + team_number)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to convert time duration (HH:MM:SS) to a timedelta object for comparison
def convert_to_timedelta(duration_str):
    hours, minutes, seconds = map(int, duration_str.split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

# Store team data in a dictionary to avoid duplicates
teams_data = {}
all_images = set()

# Fetch data for each team and ensure it's not duplicated
for team_number in team_numbers:
    if team_number not in teams_data:  # Prevent duplicates
        data = fetch_team_data(team_number)
        if data and "data" in data and data["data"]:
            teams_data[team_number] = data["data"]
            # Collect all unique image names across teams
            for image_data in data["data"]:
                all_images.add(image_data['image'])
        else:
            # If the team doesn't exist or no data is returned, mark it as missing
            teams_data[team_number] = None

# Sort the list of all images to maintain order
all_images = sorted(all_images)

# Process the data to prepare for HTML generation
processed_teams = []

for team_number, team in teams_data.items():
    if team:  # Valid team data
        total_score = 0
        images = {image: 'not started' for image in all_images}  # Pre-fill with 'not started'
        max_duration = timedelta(0)  # Initialize max duration to zero

        for image_data in team:
            images[image_data['image']] = image_data['ccs_score']
            total_score += image_data['ccs_score']

            # Update max_duration if this image's duration is greater
            image_duration = convert_to_timedelta(image_data['duration'])
            if image_duration > max_duration:
                max_duration = image_duration

        # Convert max_duration back to HH:MM:SS format for display
        max_duration_str = str(max_duration)

        processed_teams.append({
            'team_number': team[0]['team_number'],
            'images': images,
            'total_score': total_score,
            'duration': max_duration_str,  # Store the greatest duration
        })
    else:  # Team does not exist or no data was returned
        images = {image: 'not started' for image in all_images}
        processed_teams.append({
            'team_number': team_number,
            'images': images,
            'total_score': 0,
            'duration': 'not available'
        })

# Sort teams by total score (descending)
sorted_teams = sorted(processed_teams, key=lambda x: x['total_score'], reverse=True)

# HTML Template using Jinja2 with a 30-second meta-refresh
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">  <!-- Meta-refresh every 30 seconds -->
    <title>Team Scores</title>
    <style>
        body {
            background-color: black;
            color: cyan;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            color: cyan;
        }
        table, th, td {
            border: 1px solid cyan;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
    </style>
</head>
<body>
    <h1>CyberPatriot Team Scores</h1>
    <table>
        <thead>
            <tr>
                <th>Team Number</th>
                {% for image in all_images %}
                <th>{{ image }} (CCS Score)</th>
                {% endfor %}
                <th>Total Score</th>
                <th>Greatest Duration</th>
            </tr>
        </thead>
        <tbody>
            {% for team in sorted_teams %}
            <tr>
                <td>{{ team['team_number'] }}</td>
                {% for image in all_images %}
                <td>{{ team['images'][image] }}</td>
                {% endfor %}
                <td>{{ team['total_score'] }}</td>
                <td>{{ team['duration'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# Render the HTML
template = Template(html_template)
html_content = template.render(sorted_teams=sorted_teams, all_images=all_images)

# Write the HTML to a file
with open('team_scores.html', 'w') as f:
    f.write(html_content)

print("Webpage created: team_scores.html")






