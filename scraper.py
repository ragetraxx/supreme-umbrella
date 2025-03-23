import requests
from bs4 import BeautifulSoup
import re

# Base site URL
base_url = 'https://methstreams.ac'
streams_page = '/nbastreams/'  # The main NBA Streams page
headers = {'User-Agent': 'Mozilla/5.0'}

# Step 1: Fetch the NBA Streams page
response = requests.get(base_url + streams_page, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

# Step 2: Extract game titles and links
games = {}
for link in soup.find_all('a', href=True):
    href = link['href']
    if '/nbastreams/' in href:
        game_title = link.text.strip()
        game_url = base_url + href
        if game_title and game_url not in games.values():
            games[game_title] = game_url

# Step 3: Visit each game page and extract video URLs
game_videos = {}

for game_title, stream_link in games.items():
    try:
        stream_response = requests.get(stream_link, headers=headers)
        stream_response.raise_for_status()

        stream_soup = BeautifulSoup(stream_response.content, 'html.parser')

        # Extract video URL (inside <iframe> or <script>)
        video_url = None
        for iframe in stream_soup.find_all('iframe', src=True):
            if 'http' in iframe['src']:
                video_url = iframe['src']
                break

        if not video_url:
            script_tags = stream_soup.find_all('script')
            for script in script_tags:
                if script.string and 'source' in script.string:
                    match = re.search(r'source:\s*["\'](http[^"\']+)["\']', script.string)
                    if match:
                        video_url = match.group(1)
                        break

        if video_url:
            game_videos[game_title] = video_url
            print(f"Extracted video for {game_title}: {video_url}")

    except requests.RequestException as e:
        print(f"Failed to fetch {stream_link}: {e}")

# Step 4: Generate the HTML content
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rage / NBA Streams</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #111;
            color: white;
            text-align: center;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 80%;
            margin: auto;
            padding: 20px;
        }}
        .logo {{
            width: 150px;
            margin-top: 20px;
        }}
        h1 {{
            color: #ff4500;
            text-transform: uppercase;
        }}
        .game {{
            background: #222;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
        }}
        .game a {{
            color: #ffcc00;
            text-decoration: none;
            font-weight: bold;
        }}
        .game a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 20px;
            padding: 10px;
            background: #222;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="logo.png" alt="Logo" class="logo">
        <h1>NBA Games of the Day</h1>
"""

for game, video in game_videos.items():
    html_content += f"""
        <div class="game">
            <h2>{game}</h2>
            <a href="{video}" target="_blank">Watch Now</a>
        </div>
    """

html_content += """
        <div class="footer">
            <p>&copy; 2025 Rage NBA Streams. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

# Step 5: Save the HTML file
html_filename = "index.html"
with open(html_filename, 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)

print(f"🏀 Sporty-themed index.html created: {html_filename}")
