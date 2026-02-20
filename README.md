# XDownloadervideos
a tool that download all videos from X account and put it in zip file



# Setup:

pip install yt-dlp

# Basic usage:
Download all videos from @nasa
python x_video_downloader.py nasa

Limit to 10 videos:
python x_video_downloader.py nasa --limit 10

Custom output filename:
python x_video_downloader.py nasa --output my_videos.zip

Lower quality (saves space):
python x_video_downloader.py nasa --quality "bestvideo[height<=720]+bestaudio/best"

# Private account

For private accounts or when rate-limited:

Use your browser cookies (log into X first, then export)

python x_video_downloader.py username --cookies cookies.txt
