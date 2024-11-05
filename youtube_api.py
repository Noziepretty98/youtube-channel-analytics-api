### FastAPI application
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# Replace with your YouTube Data API key and channel ID
YOUTUBE_API_KEY = 'AIzaSyD5qbzQM-0nx_2TqMNdEDgdqnLBL_TndxI'
CHANNEL_ID = 'UC5qUQ7H7DO18VyNo2fRIxEw'

@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the YouTube Channel Analytics API"}

def fetch_data(url: str):
    """
    Helper function to fetch data from the YouTube API.
    
    Args:
        url (str): The API endpoint URL to fetch data from.
        
    Returns:
        dict: Parsed JSON response from the API.
        
    Raises:
        HTTPException: If the API request fails with a non-200 status code.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from YouTube API")
    return response.json()

@app.get("/channel_stats")
def get_channel_stats():
    """
    Fetch basic statistics of your YouTube channel.
    
    Returns:
        dict: A dictionary containing subscriber count, total views, and video count.
        
    Raises:
        HTTPException: If channel stats cannot be fetched.
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    data = fetch_data(url)
    
    if "items" in data and data["items"]:
        stats = data["items"][0]["statistics"]
        return {
            "subscribers": stats["subscriberCount"],
            "total_views": stats["viewCount"],
            "video_count": stats["videoCount"]
        }
    raise HTTPException(status_code=404, detail="Could not fetch channel stats")

@app.get("/latest_videos")
def get_latest_videos(max_results: int = 5, published_after: str = None):
    """
    Fetch the latest videos from your YouTube channel.
    
    Args:
        max_results (int): Number of videos to fetch (default is 5).
        published_after (str): Optional date to filter videos published after a specific date (in ISO 8601 format).
        
    Returns:
        dict: A dictionary containing a list of videos with their IDs, titles, and publication dates.
        
    Raises:
        HTTPException: If no videos are found or if videos cannot be fetched.
    """
    url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={CHANNEL_ID}&part=snippet&order=date"
    if published_after:
        url += f"&publishedAfter={published_after}"

    data = fetch_data(url)
    
    if "items" in data:
        videos = [
            {
                "video_id": item["id"].get("videoId", "N/A"),
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"]
            }
            for item in data["items"] if "videoId" in item["id"]
        ]
        return {"videos": videos[:max_results]}  # Return only the requested number of videos
    raise HTTPException(status_code=404, detail="No videos found or could not fetch videos.")

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)
