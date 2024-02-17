#pakages
from googleapiclient.discovery import build
from streamlit_option_menu import option_menu
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import unquote
from dateutil import parser
from datetime import datetime,timedelta
import io
import re
import time
import base64
import requests
import pandas as pd
import streamlit as st
import mysql.connector
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title = "YouTube data analaysis",
                   page_icon = 'youtube',
                    layout= "wide" )

st.markdown(
    "<h1 style='text-align: center; color: red; '> YouTube Data Analysis Dashboard</h1>",
    unsafe_allow_html=True
    )

#Api connection
@st.cache_data
def Api_connect():
    Api_key = "AIzaSyDoukUWd3WFQ0DzidjTTPEnuOQAww2-gRE"
    Api_services_name = "youtube"
    Api_version = "v3"

    youtube = build(Api_services_name,Api_version,developerKey=Api_key)

    return youtube

youtube = Api_connect()

#Mongodb connection string
uri = "mongodb+srv://stephanraj24:4065642@cluster0.2myxj49.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["YouTube_Warehouse"] #Define the database.

#mysql connection string

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
)
print(mydb)
mycursor = mydb.cursor(buffered=True)

# Getting ch data from URL part starts here
@st.cache_data
def extract_username_from_url(url):
    if '@' in url:
        return url.split('@')[1]
    elif 'youtube.com/watch' in url:
        match = re.search(r'(?<=\&ab_channel=)([\w%]+)', url)
        if match:
            username = unquote(match.group(1))
    return username
@st.cache_data
def search_youtube_channel(api_key, username):
    base_url = "https://youtube.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': username,
        'type': 'channel',
        'key': 'AIzaSyDoukUWd3WFQ0DzidjTTPEnuOQAww2-gRE', # Replace with your actual API key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)
@st.cache_data
def get_chennal_data(channel_id):
    request = youtube.channels().list(  
                        part="snippet,contentDetails,statistics",
                        id=channel_id
    )
    response = request.execute()

    data_list = []
    for item in response.get("items", []):
        data = {
            "Chennal_Id": item.get("id"),
            "Chennal_Name": item["snippet"]["title"],
            "Total_Subscribers": item["statistics"]["subscriberCount"],
            "Total_Views": item["statistics"]["viewCount"],
            "Total_Videos": item["statistics"]["videoCount"],
            "About_chennal": item["snippet"]["description"],
            "Playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"]
        }
        data_list.append(data)

    return data_list
@st.cache_data
def chname(channel_id):
    request = youtube.channels().list(  
                        part="snippet,contentDetails,statistics",
                        id=channel_id
    )
    response = request.execute()
    chname = (response['items'][0]['snippet']['title'])
    return chname
@st.cache_data
def get_ID_or_data(url_input):
    try:
        # Get YouTube channel URL from user
        youtube_url = url_input
        if len(youtube_url) == 24 and youtube_url.startswith('UC'):
            channel_data = get_chennal_data(youtube_url)
            disname = chname(youtube_url)
            st.success(f"Channel detail you are trying to find is {disname}. Find the details below")
            return channel_data
        elif youtube_url:
            username = extract_username_from_url(youtube_url)
            if username:
                st.success(f"Channel detail you are trying to find is {username}. Find the details below")
                result = search_youtube_channel('AIzaSyDoukUWd3WFQ0DzidjTTPEnuOQAww2-gRE', username)
                if result and 'items' in result and result['items']:
                    id = result['items'][0]['id']['channelId']
                    channel_data = get_chennal_data(id)
                    return channel_data
                else:
                    st.error("No channel found with the provided username.")
            else:
                st.error("Failed to extract username from the URL.")
        else:
            st.warning("Please Enter URL or ID.")
    except Exception as e:
        st.error("please enter valid input")

    return None
# Getting ch data from URL part ends here 

#########################################

# Getting ChPic function starts here 
@st.cache_data
def extract_username_from_url(url):
    if '@' in url:
        return url.split('@')[1]
    elif 'youtube.com/watch' in url:
        match = re.search(r'(?<=\&ab_channel=)([\w%]+)', url)
        if match:
            username = unquote(match.group(1))
    return username
@st.cache_data
def search_youtube_channel(api_key,username):
    base_url = "https://youtube.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': username,
        'type': 'channel',
        'key': 'AIzaSyDoukUWd3WFQ0DzidjTTPEnuOQAww2-gRE', # Replace with your actual API key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)

@st.cache_data
def profile_pic(Id):
  youtube = Api_connect()

  request = youtube.channels().list(
                        part="snippet,contentDetails,statistics",
                        id= Id 
    )
  response = request.execute()
  chpic = response['items'][0]['snippet']['thumbnails']['default']['url']
  return chpic
@st.cache_data
def get_Ch_Pic(url_input):
  # Get YouTube channel URL from user
  youtube_url = url_input
  if len(youtube_url) == 24 and youtube_url.startswith('UC'):
    ChPic = profile_pic(youtube_url)
    return ChPic
  elif youtube_url:
    username = extract_username_from_url(youtube_url)
    result = search_youtube_channel('AIzaSyDoukUWd3WFQ0DzidjTTPEnuOQAww2-gRE', username)
    id = (result['items'][0]['id']['channelId'])
    ChPic = profile_pic(id)
    return ChPic
  else:
    print("Invalid YouTube URL format.")

## Getting ChPic function ends here 
###################################
## Getting Video Info function starts here 
@st.cache_data    
def get_ID(url_input):
    try:
        # Get YouTube channel URL from user
        youtube_url = url_input
        if len(youtube_url) == 24 and youtube_url.startswith('UC'):
            return youtube_url
        elif youtube_url:
            username = extract_username_from_url(youtube_url)
            if username:
                result = search_youtube_channel('AIzaSyDoukUWd3WFQ0DzidjTTPEnuOQAww2-gRE', username)
                if result and 'items' in result and result['items']:
                    id = result['items'][0]['id']['channelId']
                    return id
    except Exception as e:
        st.error("please enter valid input")

    return id

#Function To get Video_ids
@st.cache_data
def Get_Video_ids(chennal_id):
    Video_ids = []
    Playlist_Id_response = youtube.channels().list(id=chennal_id,
                                    part='contentDetails').execute()

    Playlist_Id = Playlist_Id_response['items'][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    next_page_token = None
 
    while True:
        Video_id_respose = youtube.playlistItems().list(part='snippet',
                                            playlistId=Playlist_Id,
                                            maxResults=50,
                                            pageToken=next_page_token).execute()
        for i in range(len(Video_id_respose['items'])):
            Video_ids.append(Video_id_respose['items'][i]['snippet']["resourceId"]['videoId'])
        next_page_token = Video_id_respose.get('nextPageToken')

        if next_page_token is None:
            break
    return Video_ids

# Functio to fetch Video's Information using Video_ids.
@st.cache_data
def Get_Video_Info(video_ids):
    Video_Details = []
    
    for video_id in video_ids:
        Video_info_request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        Video_info_response = Video_info_request.execute()

        for item in Video_info_response['items']:
            data = dict(
                Chennal_Id = item['snippet']['channelId'],
                Chennal_Name = item['snippet']['channelTitle'],
                Video_id = item['id'],
                Video_Name = item['snippet']['title'],
                Video_Description = item['snippet'].get('description'),
                Video_Duration = item['contentDetails']['duration'],
                Tags = item['snippet'].get('tags'), 
                Video_uploaded_on = item['snippet']['publishedAt'],
                This_Video_Views = item['statistics'].get('viewCount'),
                Total_likes = item['statistics'].get('likeCount', 0),
                Comment_Count = item['statistics'].get('commentCount'),
                Favorite_Count = item['statistics'].get('favoriteCount'),
                thumbnails = item['snippet']['thumbnails']['high']['url'],
                Caption_Status = item['contentDetails']['caption'],
                Video_Quality = item['contentDetails']['definition']
            )
            Video_Details.append(data)
    return Video_Details
## Getting Video Info function ends here
########################################
## Getting Playlsit function starts here

# Functio to fetch Playlis deatils using chennal_ids.
@st.cache_data
def Get_Playlist_deatils(chennalid):
    next_page_token = None 
    playlist_data = []

    while True:
        chennal_playlist_request = youtube.playlists().list(
                                                        part = "snippet,contentDetails",
                                                        channelId = chennalid,
                                                        maxResults = 50,
                                                        pageToken = next_page_token
                                                        )
        chennal_playlist_response = chennal_playlist_request.execute()

        for item in chennal_playlist_response['items']:
            data = dict(
                        Chennal_Id = item['snippet']['channelId'],
                        Chennal_Name = item['snippet']['channelTitle'],
                        Playlist_id = item['id'],
                        Playlist_Title = item['snippet']['title'],
                        Playlist_Published_at = item ['snippet']['publishedAt'],
                        Playlist_video_count = item['contentDetails']['itemCount']
                        )
            playlist_data.append(data)
        
        next_page_token = chennal_playlist_response.get('nextPageToken')
        if next_page_token is None:
            break
    return playlist_data
## Getting Playlsit function ends here 
######################################
## Getting comments function starts here 
# Functio to fetch Video's comments deatils using Video_ids.
@st.cache_data
def Get_Video_Cmts(videoids):
    Cmt_data = []
    for Cmt_ids in videoids:
        try:
            Video_Comment_request = youtube.commentThreads().list(
                part="snippet",
                videoId=Cmt_ids,
                maxResults=50
            )
            Video_Comment_response = Video_Comment_request.execute()

            for cmts in Video_Comment_response['items']:
                data = dict(
                    Chennal_Id = cmts['snippet']['channelId'],
                    Comment_id = cmts['snippet']['topLevelComment']['id'],
                    Comment_Text = cmts['snippet']['topLevelComment']['snippet']['textDisplay'],
                    Comment_Author = cmts['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    Comment_like_count = cmts['snippet']['topLevelComment']['snippet']['likeCount'],
                    Comment_Published_At = cmts['snippet']['topLevelComment']['snippet']['publishedAt'])
                
                Cmt_data.append(data)

                # Process the comment data as needed
        except Exception as e:
            # Handle the specific exception when comments are disabled
            if 'commentsDisabled' in str(e):
                print(f"Comments are disabled for this video ({Cmt_ids}), So Skipping to next video...")
            else:
                print(f"An error occurred for video {Cmt_ids}: {e}")
    return Cmt_data

## Getting comments function ends here
######################################
## Push data to mongoDB function starts here 

#function to push feteched data to MongoDb
def Chennal_Deatils(chennal_id):
    Chennal_Data = get_chennal_data(chennal_id)[0]
    Chennal_Videos_id = Get_Video_ids(chennal_id)
    Chennal_Videos_Info = Get_Video_Info(Chennal_Videos_id)
    Chennal_Videos_Cmts_Info = Get_Video_Cmts(Chennal_Videos_id)
    Chennal_Videos_Playlist_Info = Get_Playlist_deatils(chennal_id)

    Collention = db['Chennal_Details']
    Collention.insert_one({
            "Chennal_Inforamtion" : Chennal_Data,
            "Video_Information" : Chennal_Videos_Info ,
            "Comments" : Chennal_Videos_Cmts_Info, 
            "Playlist_information" : Chennal_Videos_Playlist_Info
            })
    return "Data Uploaded Successfully"

## Push data to mongoDB function starts here
############################################
## Function to migrate the MongoDB data to sql Database starts here
#Creating Table in Mysql.
@st.cache_data
def Push_data_to_sql():
    mycursor.execute("USE YouTube_Data")

    Drop_quary = ''' drop table if exists channels'''
    mycursor.execute(Drop_quary)
    mydb.commit()

    try:
        Create_quary ='''create table if not exists channels(Chennal_Id varchar(100) primary key,
                                                            Chennal_Name varchar(100),
                                                            Total_Subscribers bigint,
                                                            Total_Views bigint,
                                                            Total_Videos bigint,
                                                            About_chennal text,
                                                            Playlist_id varchar(100)
                                                            )'''
        mycursor.execute(Create_quary)
        mydb.commit()
    except:
        print("Table already created")

    #Geting data from mongoDb then converting data into DataFrame and saving that data to SQL table.
    Ch_list = []
    db = client.YouTube_Warehouse
    records = db.Chennal_Details
    Projection = records.find({},{"_id":0,"Chennal_Inforamtion":1})

    for coll in Projection:
        Ch_list.append(coll['Chennal_Inforamtion'])

    df = pd.DataFrame(Ch_list)

    #insert values into table
    for index,row in df.iterrows():
        inser_qury = '''insert into channels(Chennal_Id,
                                            Chennal_Name,
                                            Total_Subscribers,
                                            Total_Views,
                                            Total_Videos,
                                            About_chennal,
                                            Playlist_id) values (%s,%s,%s,%s,%s,%s,%s)'''
        values = (row["Chennal_Id"],
                row['Chennal_Name'],
                row['Total_Subscribers'],
                row['Total_Views'],
                row['Total_Videos'],
                row['About_chennal'],
                row['Playlist_id']
                )
        try:
            mycursor.execute(inser_qury,values)
            mydb.commit()
        except:
            print("Values are inserted already")

mycursor.execute("USE YouTube_Data")

@st.cache_data
def Push_video_data_sql():
        Drop_quary = '''drop table if exists videos'''
        mycursor.execute(Drop_quary)
        mydb.commit()

        Create_quary ='''create table if not exists videos(Chennal_Id varchar(100),
                                                        Chennal_Name varchar(100),
                                                        Video_id varchar(100),
                                                        Video_Name varchar(100),
                                                        Video_Description text,
                                                        Video_Duration varchar(100),
                                                        Tags text,
                                                        Video_uploaded_on timestamp,
                                                        This_Video_Views bigint,
                                                        Total_likes bigint,
                                                        Comment_Count bigint,
                                                        Favorite_Count bigint,
                                                        thumbnails varchar(100),
                                                        Caption_Status varchar(100),
                                                        Video_Quality varchar(100)
                                                        )'''
        mycursor.execute(Create_quary)
        mydb.commit()

        #Geting data from mongoDb then converting data into DataFrame and saving that data to SQL table.
        VI_list = []
        db = client.YouTube_Warehouse
        records = db.Chennal_Details
        Projection = records.find({},{"_id":0,"Video_Information":1})

        for coll in Projection:
                for i in range(len(coll['Video_Information'])):   
                        VI_list.append(coll['Video_Information'][i])

                df = pd.DataFrame(VI_list)
                for index,row in df.iterrows():
                        if isinstance(row['Tags'], list):#converting if Tag is list to string with " , " adn if not the same 
                                tags_str = ','.join(row['Tags'])
                        else:
                                tags_str = row['Tags']

                        video_published_at = datetime.strptime(row['Video_uploaded_on'], '%Y-%m-%dT%H:%M:%SZ')
                        inser_qury = '''insert into videos(Chennal_Id,
                                                                Chennal_Name,
                                                                Video_id,
                                                                Video_Name,
                                                                Video_Description,
                                                                Video_Duration,
                                                                Tags,
                                                                Video_uploaded_on,
                                                                This_Video_Views,
                                                                Total_likes,
                                                                Comment_Count,
                                                                Favorite_Count,
                                                                thumbnails,
                                                                Caption_Status,
                                                                Video_Quality
                                                                ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        values = (row["Chennal_Id"],
                                row['Chennal_Name'],
                                row['Video_id'],
                                row['Video_Name'],
                                row['Video_Description'],
                                row['Video_Duration'],
                                tags_str,
                                video_published_at,
                                row['This_Video_Views'],
                                row['Total_likes'],
                                row['Comment_Count'],
                                row['Favorite_Count'],
                                row['thumbnails'],
                                row['Caption_Status'],
                                row['Video_Quality']
                                )
                        mycursor.execute(inser_qury,values)
                        mydb.commit()

@st.cache_data
def Push_playlist_data_sql():
    mycursor.execute("USE YouTube_Data")

    Drop_quary = ''' drop table if exists playlists'''
    mycursor.execute(Drop_quary)
    mydb.commit()

    try:
        Create_quary ='''create table if not exists playlists(Chennal_Id varchar(100),
                                                            Chennal_Name varchar(100),
                                                            Playlist_id varchar(100) primary key,
                                                            Playlist_Title varchar(100),
                                                            Playlist_Published_at timestamp,
                                                            Playlist_video_count bigint
                                                            )'''
        mycursor.execute(Create_quary)
        mydb.commit()
    except:
        print("Table already created")

    #Geting data from mongoDb then converting data into DataFrame and saving that data to SQL table.
    PL_list = []
    db = client.YouTube_Warehouse
    records = db.Chennal_Details
    Projection = records.find({},{"_id":0,"Playlist_information":1})

    for coll in Projection:
        for i in range(len(coll['Playlist_information'])):   
            PL_list.append(coll['Playlist_information'][i])

    df = pd.DataFrame(PL_list)

    for index,row in df.iterrows():
        playlist_published_at = datetime.strptime(row['Playlist_Published_at'], '%Y-%m-%dT%H:%M:%SZ')
        inser_qury = '''insert into playlists(Chennal_Id,
                                            Chennal_Name,
                                            Playlist_id,
                                            Playlist_Title,
                                            Playlist_Published_at,
                                            Playlist_video_count
                                            ) values (%s,%s,%s,%s,%s,%s)'''
        values = (row["Chennal_Id"],
                row['Chennal_Name'],
                row['Playlist_id'],
                row['Playlist_Title'],
                playlist_published_at,
                row['Playlist_video_count']
                )
        try:
            mycursor.execute(inser_qury,values)
            mydb.commit()
        except:
            print("Values are inserted already")

#Creating Table in Mysql.
@st.cache_data
def Push_comments_data_sql():
    mycursor.execute("USE YouTube_Data")

    Drop_quary = ''' drop table if exists comments'''
    mycursor.execute(Drop_quary)
    mydb.commit()

    try:
        Create_quary ='''create table if not exists comments(Chennal_Id varchar(100),
                                                            Comment_id varchar(100),
                                                            Comment_Text text,
                                                            Comment_Author varchar(100),
                                                            Comment_like_count int,
                                                            Comment_Published_At timestamp
                                                            )'''
        mycursor.execute(Create_quary)
        mydb.commit()
    except:
        print("Table already created")


    #Geting data from mongoDb then converting data into DataFrame and saving that data to SQL table.
    CMTS_list = []
    db = client.YouTube_Warehouse
    records = db.Chennal_Details
    Projection = records.find({},{"_id":0,"Comments":1})

    for coll in Projection:
        for i in range(len(coll['Comments'])):   
            CMTS_list.append(coll['Comments'][i])

    df = pd.DataFrame(CMTS_list)

    for index,row in df.iterrows():
        Comment_Published_At = datetime.strptime(row['Comment_Published_At'], '%Y-%m-%dT%H:%M:%SZ')
        inser_qury = '''insert into comments(Chennal_Id,
                                            Comment_id,
                                            Comment_Text,
                                            Comment_Author,
                                            Comment_like_count,
                                            Comment_Published_At
                                            ) values (%s,%s,%s,%s,%s,%s)'''
        values = (row["Chennal_Id"],
                row['Comment_id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_like_count'],
                Comment_Published_At,
                )
        try:
            mycursor.execute(inser_qury,values)
            mydb.commit()
        except:
            print("Values are inserted already")
@st.cache_data
def create_tabels():
    Push_data_to_sql()
    Push_video_data_sql()
    Push_playlist_data_sql()
    Push_comments_data_sql()
    return "Tables Created"

## Function to migrate the MongoDB data to sql Database ends here
#################################################################
## Channel and video anlaysis parts starts here

def ch_stats():
    Ch_list = []
    Statistics = []
    db = client.YouTube_Warehouse
    records = db.Chennal_Details
    Projection = records.find({}, {"_id": 0, "Chennal_Inforamtion": 1})

    for coll in Projection:
        Ch_list.append(coll['Chennal_Inforamtion'])

    for i in Ch_list:
        data = dict(Chennal_Name=i['Chennal_Name'],
                    Total_Subscribers=i['Total_Subscribers'],
                    Total_Views=i['Total_Views'],
                    Total_Videos=i['Total_Videos'],
                    )
        Statistics.append(data)
    Stats_DF = pd.DataFrame(Statistics)
    Stats_DF[['Total_Subscribers', 'Total_Views', 'Total_Videos']] = Stats_DF[
        ['Total_Subscribers', 'Total_Views', 'Total_Videos']].apply(pd.to_numeric)
    return Stats_DF


def video_stats(search_chennel_name):
    video_list = []
    Statistics = []
    db = client.YouTube_Warehouse
    records = db.Chennal_Details
    query = {"Video_Information.Chennal_Name": search_chennel_name}
    result = records.find(query)

    try:
        for i in result:
            video_list.append(i['Video_Information'])

        def convert_duration(duration_str):
            # Extract minutes and seconds using regular expression
            match = re.match(r'PT(\d+)M(\d+)S', duration_str)

            if match:
                minutes, seconds = map(int, match.groups())

                # Create a timedelta object with the extracted values
                duration = timedelta(minutes=minutes, seconds=seconds)

                # Format the timedelta object into a readable string
                formatted_duration = str(duration).split('.')[0]  # Removing microseconds
                formatted_duration = re.sub(r'^0:', '', formatted_duration)  # Remove leading '0:' if present
                formatted_duration = re.sub(r':', ' minutes and ', formatted_duration)
                formatted_duration = re.sub(r'$', ' seconds', formatted_duration)

                return formatted_duration
            else:
                return None

        def extract_month_year(timestamp_str):
            # Convert the timestamp to a datetime object
            timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
            # Extract month and year
            month_year_str = timestamp_dt.strftime("%B %Y")
            return month_year_str

        for j in video_list[0]:
            timestamp_dt = datetime.strptime(j['Video_uploaded_on'], "%Y-%m-%dT%H:%M:%SZ")
            data = dict(Video_Name=j["Video_Name"],
                        Video_uploaded_on=extract_month_year(j['Video_uploaded_on']),
                        Published_on=j['Video_uploaded_on'],
                        Published_day=timestamp_dt.day,
                        views=j['This_Video_Views'],
                        Total_likes=j['Total_likes'],
                        Comment_Count=j['Comment_Count'],
                        Video_Duration=convert_duration(j['Video_Duration'])
                        )
            Statistics.append(data)
        Stats_dF = pd.DataFrame(Statistics)
        Stats_dF[['views', 'Total_likes']] = Stats_dF[['views', 'Total_likes']].apply(pd.to_numeric)
        Stats_dF['Month'] = pd.to_datetime(Stats_dF['Video_uploaded_on']).dt.strftime('%b')
        Stats_dF['Published_day'] = pd.to_datetime(Stats_dF['Published_on']).dt.strftime('%a')
        return Stats_dF
    except Exception as e:
        comment = "sorry for the inconvenience. Please make sure that channel name you entered is available in database"
        st.error(comment)
        return None


def Subscribers_Analysis_and_Comment(Stats_DF):
    # Set the size of the plot
    sns.set(rc={'figure.figsize': (8, 6)})

    # Create a bar plot for Total Subscribers
    subscribers = sns.barplot(x='Chennal_Name', y='Total_Subscribers', data=Stats_DF, palette='viridis')
    
    # Set title for the plot
    subscribers.set_title('Subscribers Analysis')

    # Add labels for better understanding
    subscribers.set_xticklabels(subscribers.get_xticklabels(), rotation=45, ha='right')

    # Add data labels on top of the bars
    for p in subscribers.patches:
        subscribers.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2., p.get_height()),
                             ha='center', va='center', fontsize=10, color='black', xytext=(0, 10),
                             textcoords='offset points')

    # Identify the channel with the highest number of subscribers
    max_subscribers_channel = Stats_DF.loc[Stats_DF['Total_Subscribers'].idxmax()]['Chennal_Name']

    # Comment about the analysis
    comment = (
        f"The channel with the highest number of subscribers is '{max_subscribers_channel}' with "
        f"{Stats_DF['Total_Subscribers'].max():,} subscribers."
    )
    return comment


def Views_Analysis(Stats_DF):
    # Set the size of the plot
    sns.set(rc={'figure.figsize': (8, 6)})

    # Create a bar plot for Total Views
    views = sns.barplot(x='Chennal_Name', y='Total_Views', data=Stats_DF, palette='viridis')

    # Set title for the plot
    views.set_title("Views Analysis")

    # Add labels for better understanding
    views.set_xticklabels(views.get_xticklabels(), rotation=45, ha='right')

    # Add data labels on top of the bars
    for p in views.patches:
        views.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center', fontsize=10, color='black', xytext=(0, 10),
                       textcoords='offset points')

    # Identify the channel with the highest and lowest number of views
    max_views_channel = Stats_DF.loc[Stats_DF['Total_Views'].idxmax()]['Chennal_Name']
    min_views_channel = Stats_DF.loc[Stats_DF['Total_Views'].idxmin()]['Chennal_Name']

    # Comment about the analysis
    comment = (
        f"The channel with the highest number of views is '{max_views_channel}' with "
        f"{Stats_DF['Total_Views'].max():,} views. The channel with the lowest number of views is "
        f"'{min_views_channel}' with {Stats_DF['Total_Views'].min():,} views."
    )
    return comment


def Videos_Analysis(Stats_DF):
    # Set the size of the plot
    sns.set(rc={'figure.figsize': (8, 6)})

    # Create a bar plot for Total Videos
    videos = sns.barplot(x='Chennal_Name', y='Total_Videos', data=Stats_DF, palette='viridis')
    videos.set_title("Videos analysis")
    videos.set_xticklabels(videos.get_xticklabels(), rotation=45, ha='right')

    # Add labels on top of the bars
    for index, row in Stats_DF.iterrows():
        videos.text(row.name, row['Total_Videos'], row['Total_Videos'], color='black', ha="center")

    # Identify the channel with the highest and lowest number of videos
    max_videos_channel = Stats_DF.loc[Stats_DF['Total_Videos'].idxmax()]['Chennal_Name']
    min_videos_channel = Stats_DF.loc[Stats_DF['Total_Videos'].idxmin()]['Chennal_Name']

    # Comment about the analysis
    comment = (
        f"The channel with the highest number of videos is '{max_videos_channel}' with "
        f"{Stats_DF['Total_Videos'].max():,} videos. The channel with the lowest number of videos is "
        f"'{min_videos_channel}' with {Stats_DF['Total_Videos'].min():,} videos."
    )
    return comment

def Best_Performing_Video(Stats_dF):
    if Stats_dF is None:
        print("Channal is not selected")
        return
    # Sort the DataFrame by the views column in descending order and select the top 10 rows
    Top10_videos = Stats_dF.sort_values(by='views', ascending=False).head(10).reset_index(drop=True)

    # Set the size of the plot
    sns.set(rc={'figure.figsize': (8, 6)})

    # Create a bar plot for the views and video name columns
    top_video = sns.barplot(x='views', y='Video_Name', data=Top10_videos, palette='viridis')
    top_video.set_title('Best Performing Video')

    # Identify the video with the highest number of views
    max_views_video = Top10_videos.loc[0, 'Video_Name']

    # Comment about the analysis
    comment = f"The best performing video is '{max_views_video}' with {Top10_videos['views'].max():,} views."
    return comment

def Least_Performing_Video(Stats_dF):
    if Stats_dF is None:
        print("Channal is not selected")
        return
    # Sort the DataFrame by views in ascending order, select the top 10 least viewed videos, and reset the index
    Top10_videos = Stats_dF.sort_values(by='views', ascending=True).head(10).reset_index(drop=True)
    
    # Set seaborn plot size
    sns.set(rc={'figure.figsize': (8, 6)})
    
    # Create a bar plot to visualize the least performing videos
    top_least_video = sns.barplot(x='views', y='Video_Name', data=Top10_videos, palette='viridis')
    top_least_video.set_title('Least Performed Video')

    # Comment about the analysis
    comment = f"The least performing video is '{Top10_videos.loc[Top10_videos['views'].idxmin(), 'Video_Name']}' with {Top10_videos['views'].min():,} views."
    return comment

def videos_count_in_month(Stats_dF):
    if Stats_dF is None:
        print("Channel is not selected")
        return
    
    # Define the order of months
    sort_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Count the number of videos per month, reindex to include all months, and fill missing values with 0
    Videos_per_month = Stats_dF['Month'].value_counts().reindex(sort_order, fill_value=0).reset_index()
    
    # Rename columns for clarity
    Videos_per_month.columns = ['Month', 'Video_Count']
    
    # Find the month with the highest number of video uploads
    max_month = Videos_per_month.loc[Videos_per_month['Video_Count'].idxmax()]['Month']
    
    # Set seaborn plot size
    sns.set(rc={'figure.figsize': (8, 6)})
    
    # Create a bar plot to visualize the number of videos per month
    videos_count = sns.barplot(x='Month', y='Video_Count', data=Videos_per_month, palette='viridis')
    videos_count.set_title("Videos per month")

    # Add data labels on top of the bars
    for index, row in Videos_per_month.iterrows():
        videos_count.text(row.name, row.Video_Count, str(row.Video_Count), color='black', ha="center")
    
    # Comment about the analysis
    comment = f"The month with the highest number of video uploads is {max_month}."
    return comment

def videos_per_day(Stats_dF):
    if Stats_dF is None:
        print("Channal is not selected")
        return
    # Define the sort order for the published days
    sort_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # Group the DataFrame by the published day and count the number of videos
    published_day_counts = Stats_dF.groupby('Published_day')['Published_day'].count()

    # Reindex the Series to match the sort order and convert it to a DataFrame
    published_day_counts = published_day_counts.reindex(sort_order).to_frame(name='count')

    # Set the size of the plot
    sns.set(rc={'figure.figsize': (8, 6)})

    # Create a bar plot for the video upload frequency
    videos_per_day = sns.barplot(x='Published_day', y='count', data=published_day_counts, palette='viridis')
    videos_per_day.set_title("Video upload frequency in day")
    
    # Add data labels on top of the bars
    for index, row in published_day_counts.iterrows():
        videos_per_day.text(row.name, row['count'], str(row['count']), color='black', ha="center")

    # Calculate the day with the maximum and minimum video uploads
    max_day = published_day_counts['count'].idxmax()
    min_day = published_day_counts['count'].idxmin()

    # Comment about the analysis
    comment = f"Here we can see that he/she uploading more videos on {max_day}'s and less videos on {min_day}'s."
    return comment


def ch_stats_drop_down():
    Ch_list = []
    Statistics = []
    db = client.YouTube_Warehouse
    records = db.Chennal_Details
    Projection = records.find({}, {"_id": 0, "Chennal_Inforamtion": 1})

    for coll in Projection:
        Ch_list.append(coll['Chennal_Inforamtion'])

    for i in Ch_list:
        data = dict(Chennal_Name=i['Chennal_Name'])
        Statistics.append(data)
    Stats_DF = pd.DataFrame(Statistics)
    return Stats_DF

def analysis_part():
    ch_stats_df = ch_stats()
    Subscribers_Analysis_and_Comment(ch_stats_df)
    plt.show()
    Views_Analysis(ch_stats_df)
    plt.show()
    Videos_Analysis(ch_stats_df)
    plt.show()
    plt.tight_layout()

def Video_Analysis_part():
    video_stats_df = video_stats()
    Best_Performing_Video(video_stats_df)
    plt.show()
    Least_Performing_Video(video_stats_df)
    plt.show()
    videos_count_in_month(video_stats_df)
    plt.show()
    videos_per_day(video_stats_df)
    plt.show()
    plt.tight_layout()

## Channel and video analysis part ends here
## Streamlit dashbard app starts here
st.set_option('deprecation.showPyplotGlobalUse', False)
with st.container():
    selected = option_menu(
        menu_title= None,
        options=["🏠 Home", "⚙️ Fetch and Export Data", "SQL Analysis","Channel Analysis","Video Analysis"],
        icons= ['#','##','filetype-sql','bar-chart-line-fill','graph-up-arrow'],
        menu_icon = None,
        default_index=0,
        orientation="horizontal"
        )
    
if selected == "🏠 Home":
    st.markdown(
    "<h2 style='text-align: center;'> Welcome to YouTube Data Harvesting and Warehousing Project </h2>",
    unsafe_allow_html=True
    )
    # Title and Description
    st.markdown("This interactive dashboard empowers you to explore and analyze data from multiple YouTube channels effortlessly. Whether you're a content creator, marketer, or analyst, this tool provides valuable insights to inform your decisions and strategies.")

    # Key Features Section
    st.header("Key Features:")
    st.markdown("""
    1. **Retrieve Channel Data**: Enter a YouTube channel ID to access essential metrics such as channel name, subscriber count, total video count, playlist ID, video ID, likes, dislikes, and comments for each video.
    
    2. **Store Data in MongoDB**: Seamlessly store channel data in a MongoDB data lake, ensuring efficient management of unstructured and semi-structured data.

    3. **Migrate to SQL Database**: Effortlessly migrate data from the MongoDB data lake to a SQL database for comprehensive storage and analysis.

    4. **Advanced SQL Queries**: Perform SQL queries to extract valuable insights and trends from the stored channel data.

    5. **Intuitive Data Visualization**: Utilize Streamlit's data visualization capabilities to create interactive charts and graphs, enabling easy interpretation and analysis of the retrieved data.
    """)

    # Get Started Section
    st.header("Get Started:")
    st.markdown("Simply navigate through the menu options to explore the various functionalities of the dashboard:")
    st.markdown("- **Fetch and Eport Data**: From this section, we can get channels data using channels unique ID or YouTube link. And we can store the data to MongoDB from that Migrate SQL database")
    st.markdown("- **SQL**: Explore and retrieve data from the SQL database using different search options.")
    st.markdown("- **Channel analysis**: From this section we gonna explore YouTube Channels trends of your favorite YouTube creators! with comparing each others")
    st.markdown("- **Video analysis**: From this section we gonna explore analysis in videos form the their channel")

    # About the Project Section
    st.header("About the Project:")
    st.markdown("""
    This project leverages Streamlit, Google API, MongoDB, and SQL databases to deliver a seamless and intuitive user experience for YouTube data analysis. Designed with simplicity and functionality in mind, our dashboard empowers users to make informed decisions based on comprehensive channel insights.
    """)
    st.markdown("[Google Developer Console](https://console.cloud.google.com/cloud-resource-manager?authuser=1)")
    st.markdown("[Youtube API Reference](https://developers.google.com/youtube/v3/getting-started)")
    st.markdown("[Streamlit Documentation](https://docs.streamlit.io/library/api-reference)")
if selected == "⚙️ Fetch and Export Data":
    url_input = st.text_input("Paste Youtube URL or Channel ID")
    if not url_input:
        st.warning("Please paste URL or ID to Fetch Data")
    else:    
        loading_text = "Loading"
        bar = st.progress(0, text= loading_text)
        for loading_bar in range(100):
            time.sleep(0.01)
            bar.progress(loading_bar + 1, text = loading_text)
        time.sleep(1)
        bar.empty() 
        data = get_ID_or_data(url_input)
        df = pd.DataFrame(data)
        transpose = df.transpose()
        transpose.columns = ["Channel Basic Details"]
        col1,col2,col3,col4,col5 = st.columns(5)
        with col1:
            profile_Pic = get_Ch_Pic(url_input)
            if profile_Pic is not None:
                st.subheader("Channel Profile Picture")
                st.image(profile_Pic,width = 250)
        with col2:
            if transpose is not None and not transpose.empty:
                st.subheader("Channel Details")
                st.write(transpose)
        with col3:
            id = get_ID(url_input)
            Video_id = Get_Video_ids(id)
            video_info = Get_Video_Info(Video_id)
            df2 = pd.DataFrame(video_info)
            if df2 is not None and not df2.empty:
                st.subheader("Video Details")
                st.write(df2)
        with col4:
            playlistinfo = Get_Playlist_deatils(id)
            df3 = pd.DataFrame(playlistinfo)
            if df3 is not None and not df3.empty:
                st.subheader("Playlist Details")
                st.write(df3)
        with col5:
            commentsinfo = Get_Video_Cmts(Video_id)
            df4 = pd.DataFrame(commentsinfo)
            if df4 is not None and not df4.empty:
                st.subheader("Comment Details")
                st.write(df4)         

        if st.button("Store data in a MongoDB",type = "primary"):
            push_data_mongodb = Chennal_Deatils(id)
            if push_data_mongodb is not None:
                st.success("Data Uploaaded To MongoDb Successfully")
        
        if st.button("Migrate data to SQL data warehouse", type = "primary" ):
            sqltable = create_tabels()
            if sqltable is not None:
                st.success("Data Migrated to SQL Successfully")
         # Add download button
        if st.button("Download Data as CSV", type="primary"):
            # Create an ExcelWriter object
            output = io.BytesIO()
            
            # Create a Pandas ExcelWriter object using XlsxWriter engine
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            
            # Write each DataFrame to a separate sheet
            df.to_excel(writer, sheet_name='Data')
            transpose.to_excel(writer, sheet_name='Transpose')
            df2.to_excel(writer, sheet_name='Video_Info')
            df3.to_excel(writer, sheet_name='Playlist_Info')
            df4.to_excel(writer, sheet_name='Comments_Info')
            
            # Close the Pandas ExcelWriter object
            writer.close()
            
            # Set the file pointer to the beginning of the stream
            output.seek(0)
            
            # Generate a link for downloading the Excel file
            excel_data = output.read()
            b64 = base64.b64encode(excel_data).decode()
            link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="fetched_data.xlsx">Download Excel file</a>'
            st.markdown(link, unsafe_allow_html=True)

if selected == "SQL Analysis":
    questions = st.selectbox("Select your question",("1. What are the names of all the videos and their corresponding channels?",
                                                "2. Which channels have the most number of videos, and how many videos do they have?",
                                                "3. What are the top 10 most viewed videos and their respective channels?",
                                                "4. How many comments were made on each video, and what are their corresponding video names?",
                                                "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
                                                "6. What is the total number of likes for each video, and what are their corresponding video names?",
                                                "7. What is the total number of views for each channel, and what are their corresponding channel names?",
                                                "8. What are the names of all the channels that have published videos in the year 2022?",
                                                "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                                                "10. Which videos have the highest number of comments, and what are their corresponding channel names?")
                                                )

    col1,col2,col3 = st.columns([1,2,1])
    if questions == "1. What are the names of all the videos and their corresponding channels?": 
        query_1 = '''SELECT Video_Name AS "Video Title", Chennal_Name AS "Channel Name" FROM videos'''
        mycursor.execute(query_1)
        mydb.commit()
        t1 = mycursor.fetchall()
        df1 = pd.DataFrame(t1, columns=["Video Title", "Channel Name"])
        with col2:
            st.write(df1)
    elif questions == "2. Which channels have the most number of videos, and how many videos do they have?":
        query_2 = '''SELECT Chennal_Name as "Channel Name",Total_Videos as "Total Videos" FROM channels ORDER BY Total_Videos DESC'''
        mycursor.execute(query_2)
        mydb.commit()
        t2 = mycursor.fetchall()
        df2 = pd.DataFrame(t2, columns=["Channel Name","Total Videos"])
        with col2:
            st.write(df2)
    elif questions == "3. What are the top 10 most viewed videos and their respective channels?":
        query_3 = '''
                SELECT DISTINCT `Chennal_Name` as "Channel Name", 
                `Video_Name` as "Video Name", 
                `This_Video_Views` as "Video Views"
                FROM videos
                WHERE This_Video_Views IS NOT NULL
                ORDER BY This_Video_Views DESC
                LIMIT 10;
        '''
        mycursor.execute(query_3)
        mydb.commit()
        t3 = mycursor.fetchall()
        df3 = pd.DataFrame(t3, columns=["Channel Name","Video Name","Video Views"])
        with col2:
            st.write(df3)
    elif questions == "4. How many comments were made on each video, and what are their corresponding video names?":
        query_4 = '''
                SELECT `Chennal_Name` as "Channel Name" ,
                `Video_Name` as "Video Name",
                `Comment_Count` as "Comments Count"
                FROM videos 
                WHERE Comment_Count is NOT null
                '''
        mycursor.execute(query_4)
        mydb.commit()
        t4 = mycursor.fetchall()
        df4 = pd.DataFrame(t4, columns=["Channel Name","Video Name","Comments Count"])
        with col2:
            st.write(df4)
    elif questions == "5. Which videos have the highest number of likes, and what are their corresponding channel names?":
        query_5 = '''
                SELECT `Chennal_Name` as "Channel Name",`Video_Name` as "Video Name" , MAX(`Total_likes`) as "Highest number of likes" 
                FROM videos
                '''
        mycursor.execute(query_5)
        mydb.commit()
        t5 = mycursor.fetchall()
        df5 = pd.DataFrame(t5, columns=["Channel Name","Video Name","Highest number of likes"])
        with col2:
            st.write(df5)
    elif questions == "6. What is the total number of likes for each video, and what are their corresponding video names?":
        query_6 = '''
                SELECT `Chennal_Name` as "Channel Name",`Video_Name` as "Video Name",`Total_likes` as "Total likes"
                FROM videos
                '''
        mycursor.execute(query_6)
        mydb.commit()
        t6 = mycursor.fetchall()
        df6 = pd.DataFrame(t6, columns=["Channel Name","Video Name","Total likes"])
        with col2:
            st.write(df6)
    elif questions == "7. What is the total number of views for each channel, and what are their corresponding channel names?":
        query_7 = '''
                SELECT `Chennal_Name` as "Channel Name",`Total_Views` as "Total Views"
                FROM channels 
                ORDER BY Total_Views DESC
                '''
        mycursor.execute(query_7)
        mydb.commit()
        t7 = mycursor.fetchall()
        df7 = pd.DataFrame(t7, columns=["Channel Name","Total Views"])
        with col2:
            st.write(df7)
    elif questions == "8. What are the names of all the channels that have published videos in the year 2022?":
        query_8 = '''
                SELECT `Chennal_Name` as "Channel Name" ,`Video_Name` as "Video Name" ,`Video_uploaded_on` as "published in year 2022"
                FROM videos 
                WHERE YEAR(`Video_uploaded_on`) = 2022
                '''
        mycursor.execute(query_8)
        mydb.commit()
        t8 = mycursor.fetchall()
        df8 = pd.DataFrame(t8, columns=["Channel Name","Video Name","published in year 2022"])
        with col2:
            st.write(df8)
    elif questions == "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        query_9 = '''
            SELECT Chennal_Name as "Channel Name",
                SEC_TO_TIME(AVG(TIME_TO_SEC(
                SUBSTRING(`Video_Duration`, 3, 2) * 60 + 
                SUBSTRING(`Video_Duration`, 6, 2)
                ))) as "Average Duration"
        FROM videos
        GROUP BY `Chennal_Name`;
                '''
        mycursor.execute(query_9)
        mydb.commit()
        t9 = mycursor.fetchall()
        df9 = pd.DataFrame(t9, columns=["Channel Name","Average Duration"])
        with col2:
            st.write(df9)
    elif questions == "10. Which videos have the highest number of comments, and what are their corresponding channel names?":
        query_10 = '''
            SELECT `Chennal_Name` as "Channel Name",`Video_Name` as "Video Name", SUM(`Comment_Count`) as "Highest Number of Comments"
            from videos
            GROUP BY `Chennal_Name`
            ORDER  BY SUM(`Comment_Count`)DESC
            '''
        mycursor.execute(query_10)
        mydb.commit()
        t10 = mycursor.fetchall()
        df10 = pd.DataFrame(t10, columns=["Channel Name","Video Name","Highest Number of Comments"])
        with col2:
            st.write(df10)

if selected == "Channel Analysis":
    st.subheader("🔍 Let's explore YouTube Channels trends, and storiesbehind your favorite YouTube creators!")
    st.subheader("##")
    st.markdown("In this section, we are going to compare the channels details which are stored in our database")
    st.subheader("##")
    col1,col2,col3 = st.columns([1,2,1])
    # Channel statistics analysis
    ch_stats_df = ch_stats()
    Subscribers_Analysis_and_Comment(ch_stats_df)
    subcomment = Subscribers_Analysis_and_Comment(ch_stats_df)
    with col2:
        st.success(subcomment)
        st.pyplot()
    Views_Analysis(ch_stats_df)
    viewscomment = Views_Analysis(ch_stats_df)
    with col2:
        st.success(viewscomment)
        st.pyplot()
    Videos_Analysis(ch_stats_df)
    videoscomment = Videos_Analysis(ch_stats_df)
    with col2:
        st.success(videoscomment)
        st.pyplot()

if selected == "Video Analysis":
    st.subheader("🔍 Let's explore YouTube Channels trends, and storiesbehind your favorite YouTube creators!")
    st.subheader("##")
    st.markdown("In this section, we are going to compare the video statistics which are stored in our database")
    st.subheader("##")
    # Video statistics analysis
    drop_down = ch_stats_drop_down()
    search_chennel_name = st.selectbox("Select a Channel for analysis", drop_down['Chennal_Name'].tolist())
    col1,col2,col3 = st.columns([1,2,1])
    if search_chennel_name:
        video_stats_df = video_stats(search_chennel_name)
        Best_Performing_Video(video_stats_df)
        BPVcmts = Best_Performing_Video(video_stats_df)
        with col2:
            st.success(BPVcmts)
            st.pyplot()
        Least_Performing_Video(video_stats_df)
        LPVcmts = Least_Performing_Video(video_stats_df)
        with col2:  
            st.success(LPVcmts)
            st.pyplot()
        videos_count_in_month(video_stats_df)
        videocountcmts = videos_count_in_month(video_stats_df)
        with col2:
            st.success(videocountcmts)
            st.pyplot()
        videos_per_day(video_stats_df)
        videosperdaycmts = videos_per_day(video_stats_df)
        with col2:
            st.success(videosperdaycmts)
            st.pyplot()

