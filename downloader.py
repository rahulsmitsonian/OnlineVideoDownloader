# # downloader.py: Logic to download YouTube videos
# import yt_dlp

# class YouTubeDownloader:
#     def __init__(self, url):
#         self.url = url

#     def download(self, output_path='.'):
#         ydl_opts = {
#             'format': 'bestvideo+bestaudio/best',
#             'outtmpl': f'{output_path}/%(title)s.%(ext)s',
#             'merge_output_format': 'mp4',
#         }
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([self.url])
#         print("Download complete.")

# This file is not required for running the application and can be deleted.