import browser_cookie3
import urllib.request
import pandas as pd
import requests
import shutil
import json
import sys
from datetime import datetime

with open('course_dump_1549407800880.json', 'r') as dump:
    data = json.load(dump)


videos = pd.DataFrame(data['videos'])
courses = pd.DataFrame(data['courses'])

# Create courses DataFrame
full_list = pd.DataFrame(columns = ['course', 'releaseDate', 'role', 'strategyUUID',
                                 'strategyTitle', 'assignmentUUID', 'assignmentTitle',
                                 'reviewUUID', 'reviewTitle'])
# Create boolean list of valid courses
bool = courses['Phase'] == 'finalized'
# Limit courses to the valid ones
courses = courses[bool]

# Turn dates in to human-readable
dateList = [datetime.utcfromtimestamp(int(X)/1000).strftime('%Y.%m.%d')
            for X in courses['Scheduled Release']]

# Seed dataframe with transferables
full_list['course'] = courses['Title']
full_list['releaseDate'] = dateList
full_list['role'] = courses['Role']



# Fully complete DataFrame
for i, row in videos.iterrows():
    # Find the data of the video and place in courses DateFrame
    title = row['Video Title']
    type = row['Type']
    UUID = row['UUID']

    # Change data in DF
    full_list.loc[full_list['course'] == row['Course'], type+'UUID'] = UUID
    full_list.loc[full_list['course'] == row['Course'], type+'Title'] = title

print(full_list.to_string())

#########################################
# Start actually downloading stuff
#########################################
# Get cookies from chrome, so you're logged in
cj = browser_cookie3.chrome()

# Define download function
def downloadVideo(m3u8URL, filename):
    # Make file name compatible
    filename = filename.replace('/', ' or ')
    filename = filename[:10] + filename[10:].replace(':', '')
    # Get m3u8 file from server
    r = requests.get(m3u8URL, cookies = cj)

    # Turn in to readable string
    m3u8file = r.content.decode("utf-8")

    # Split string in to lines
    m3u8lines = m3u8file.splitlines()

    # Create list of .ts files
    urllist = []
    for line in m3u8lines:
        if line[:4] == '#EXT':
            continue
        urllist.append(line)

    # Combine the .ts files in one big one.

    print("starting to merge file:", filename)
    with open(filename, 'wb') as merged:
        for i, ts_url in enumerate(urllist):
            # Write to temporary file
            ts_file = r'D:\- Coding\SkillcappedScraper\temp.ts'
            urllib.request.urlretrieve(ts_url, ts_file)
            # Merge temporary file with main file
            with open(ts_file, 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)

            print('Merged file {} out of {}'.format(i, len(urllist)), end='\r')

for i, course in full_list[43:].iterrows():
    fileString = 'J:\\Educational\\League\\Missions'
    role = course['role']
    date = course['releaseDate']
    fileString = fileString + '\\' + role + '\\' + role + '-' + date + '-'

    baseURL = 'https://www.skill-capped.com/lol/api/dailyvideo/'

    # Make strategy file
    stratFileString = fileString + 'strategy' + '-' + course['strategyTitle'] + '.ts'
    stratURL = baseURL + course['strategyUUID'] + '/4500.m3u8'

    downloadVideo(stratURL, stratFileString)

    # Make assignment file
    assFileString = fileString + 'assignment' + '-' + course['assignmentTitle'] + '.ts'
    assURL = baseURL + course['assignmentUUID'] + '/4500.m3u8'

    downloadVideo(assURL, assFileString)

    # Make review file
    reviewFileString = fileString + 'review' + '-' + course['reviewTitle'] + '.ts'
    reviewURL = baseURL + course['reviewUUID'] + '/4500.m3u8'

    downloadVideo(reviewURL, reviewFileString)
