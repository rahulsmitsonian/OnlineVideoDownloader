# main.py: Entry point for YouTubeDownloader
from downloader import YouTubeDownloader

def main():
    url = input("Enter YouTube video URL: ")
    downloader = YouTubeDownloader(url)
    downloader.download()

if __name__ == "__main__":
    main()