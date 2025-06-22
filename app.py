import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import os
from PIL import Image, ImageTk
import io
import requests
import yt_dlp 
import sys
from bs4 import BeautifulSoup

# Set default to myDownloader in Windows Documents folder
DEFAULT_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'myDownloader')

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

class App:
    def __init__(self, root):
        self.root = root
        root.title("YouTube Video Downloader")
        root.geometry("420x420")
        root.resizable(False, False)

        self.selected_folder = DEFAULT_FOLDER
        self.thumbnail_img = None  # To keep a reference to the image

        # Main frame for padding
        main_frame = tk.Frame(root, bg="#f8f8f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Title label
        title_label = tk.Label(main_frame, text="YouTube Video Downloader", font=("Arial", 15, "bold"), bg="#f8f8f8", fg="#333")
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 12), sticky="ew")

        # URL input row
        url_label = tk.Label(main_frame, text="YouTube URL:", font=("Arial", 10), bg="#f8f8f8")
        url_label.grid(row=1, column=0, sticky="e", padx=(0, 6), pady=3)
        self.url_entry = tk.Entry(main_frame, width=28, font=("Arial", 10))
        self.url_entry.grid(row=1, column=1, sticky="ew", pady=3)
        self.ok_button = tk.Button(main_frame, text="OK", width=5, command=self.show_thumbnail)
        self.ok_button.grid(row=1, column=2, padx=(6, 0), pady=3)

        # Folder selection row
        folder_label_label = tk.Label(main_frame, text="Selected folder:", font=("Arial", 9), fg="#555", bg="#f8f8f8", anchor="w")
        folder_label_label.grid(row=2, column=0, sticky="e", padx=(0, 4), pady=(0, 7))
        self.folder_entry = tk.Entry(main_frame, font=("Arial", 9), width=38, state='readonly', readonlybackground="#f8f8f8", fg="#555")
        self.folder_entry.grid(row=2, column=1, sticky="ew", pady=(0, 7))
        self.folder_entry.config(state='normal')
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.selected_folder)
        self.folder_entry.config(state='readonly')
        self.choose_folder_button = tk.Button(main_frame, text="Choose Folder", width=12, command=self.choose_folder)
        self.choose_folder_button.grid(row=2, column=2, sticky="w", padx=(6, 0), pady=(0, 7))

        # Preview section
        preview_label = tk.Label(main_frame, text="Preview:", font=("Arial", 10, "bold"), bg="#f8f8f8")
        preview_label.grid(row=3, column=0, sticky="ne", padx=(0, 6))
        # Create a blank image for initial placeholder
        self.blank_img = ImageTk.PhotoImage(Image.new('RGB', (160, 90), color='#eaeaea'))
        self.preview_img_label = tk.Label(main_frame, image=self.blank_img, bg="#eaeaea", width=160, height=90, relief=tk.SUNKEN, bd=1)
        self.preview_img_label.grid(row=3, column=1, columnspan=2, sticky="w", pady=(0, 7))

        # Progress bar and percent (new row, full width)
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100, length=260)
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=(0, 2), sticky="ew", padx=(0, 0))
        self.progress_label = tk.Label(main_frame, text="0%", font=("Arial", 9), bg="#f8f8f8")
        self.progress_label.grid(row=4, column=2, sticky="e", padx=(6, 0))

        # Status bar for file size
        self.status_var = tk.StringVar()
        self.status_var.set("")
        self.status_bar = tk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9), bg="#f8f8f8", anchor="w", fg="#666")
        self.status_bar.grid(row=6, column=0, columnspan=4, sticky="ew", pady=(10, 0))

        # Log area below status bar
        self.log_text = tk.Text(main_frame, height=4, font=("Consolas", 9), bg="#f4f4f4", fg="#222", state='disabled', wrap='word')
        self.log_text.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(4, 0), padx=(0, 0))

        # Download, Restore, and Close buttons (new row, centered)
        button_frame = tk.Frame(main_frame, bg="#f8f8f8")
        button_frame.grid(row=5, column=0, columnspan=3, pady=(18, 0))
        self.download_button = tk.Button(button_frame, text="Download", width=12, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.download_video)
        self.download_button.pack(side=tk.LEFT, padx=(0, 8))
        self.restore_button = tk.Button(button_frame, text="Restore", width=10, command=self.restore_form)
        self.restore_button.pack(side=tk.LEFT, padx=(0, 8))
        self.close_button = tk.Button(button_frame, text="Close", width=8, command=root.destroy)
        self.close_button.pack(side=tk.LEFT)

        # Center columns
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=0)
        main_frame.grid_columnconfigure(3, weight=0)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.selected_folder = folder
            self.folder_entry.config(state='normal')
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, self.selected_folder)
            self.folder_entry.config(state='readonly')

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def show_thumbnail(self):
        # Clear log when OK is clicked
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        try:
            self.log(f"Fetching info for: {url}")
            ydl_opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumb_url = info.get('thumbnail')
                if thumb_url:
                    self.log("Thumbnail found, downloading preview image...")
                    response = requests.get(thumb_url)
                    img_data = response.content
                    img = Image.open(io.BytesIO(img_data))
                    img = img.resize((160, 90), Image.LANCZOS)
                    self.thumbnail_img = ImageTk.PhotoImage(img)
                    self.preview_img_label.config(image=self.thumbnail_img)
                    self.log("Preview image loaded.")
                else:
                    self.preview_img_label.config(image=self.blank_img, text='No thumbnail found')
                    self.log("No thumbnail found.")
        except Exception as e:
            self.preview_img_label.config(image=self.blank_img, text=f'Error: {str(e)}')
            self.log(f"Error: {str(e)}")

    def download_video(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL or webpage.")
            return
        self.preview_img_label.config(image=self.blank_img, text='Downloading...')
        self.progress.set(0)
        self.progress_label.config(text="0%")
        self.status_var.set("")
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

        downloaded_file_size = [0]

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('downloaded_bytes', 0) / max(d.get('total_bytes', 1), 1) * 100 if d.get('total_bytes') else 0
                self.progress.set(percent)
                self.progress_label.config(text=f"{percent:.1f}%")
                if d.get('downloaded_bytes'):
                    size_mb = d['downloaded_bytes'] / 1024 / 1024
                    self.status_var.set(f"Downloaded: {size_mb:.2f} MB")
                if d.get('speed'):
                    speed = d['speed'] / 1024 if d['speed'] else 0
                    msg = f"Speed: {speed:.2f} KB/s"
                    self.log(msg)
                if d.get('eta'):
                    msg = f"ETA: {d['eta']}s"
                    self.log(msg)
                self.root.update_idletasks()
            elif d['status'] == 'finished':
                self.progress.set(100)
                self.progress_label.config(text="100%")
                if d.get('total_bytes'):
                    size_mb = d['total_bytes'] / 1024 / 1024
                    self.status_var.set(f"File size: {size_mb:.2f} MB")
                    downloaded_file_size[0] = d['total_bytes']
                elif d.get('downloaded_bytes'):
                    size_mb = d['downloaded_bytes'] / 1024 / 1024
                    self.status_var.set(f"File size: {size_mb:.2f} MB")
                    downloaded_file_size[0] = d['downloaded_bytes']
                self.log("Download finished.")
                self.root.update_idletasks()

        def is_youtube_url(link):
            return 'youtube.com/watch' in link or 'youtu.be/' in link

        def get_youtube_links_from_page(page_url):
            try:
                resp = requests.get(page_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if is_youtube_url(href):
                        if href.startswith('/watch'):
                            href = 'https://www.youtube.com' + href
                        links.add(href)
                return list(links)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch webpage: {e}")
                return []

        def get_all_links_from_page(page_url):
            try:
                resp = requests.get(page_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http'):
                        links.add(href)
                return list(links)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch webpage: {e}")
                return []

        # Download logic
        try:
            self.progress.set(0)
            self.progress_label.config(text="0%")
            self.status_var.set("")
            self.log(f"Starting download: {url}")
            self.root.update_idletasks()
            ydl_opts = {
                'outtmpl': f'{self.selected_folder}/%(title)s.%(ext)s',
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'progress_hooks': [progress_hook],
                'quiet': True,
                'logger': self
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.preview_img_label.config(image=self.blank_img, text=f"Download complete!\nSaved to: {self.selected_folder}")
            if downloaded_file_size[0]:
                size_mb = downloaded_file_size[0] / 1024 / 1024
                self.status_var.set(f"Last file size: {size_mb:.2f} MB")
            self.log("Download complete.")
        except Exception as e:
            self.preview_img_label.config(image=self.blank_img, text=f"Error: {str(e)}")
            self.status_var.set("")
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    # yt-dlp logger interface
    def debug(self, msg): self.log(msg)
    def info(self, msg): self.log(msg)
    def warning(self, msg): self.log("WARNING: " + msg)
    def error(self, msg): self.log("ERROR: " + msg)

    def restore_form(self):
        self.url_entry.delete(0, tk.END)
        self.preview_img_label.config(image=self.blank_img, text='')
        self.progress.set(0)
        self.progress_label.config(text="0%")
        self.status_var.set("")
        self.selected_folder = DEFAULT_FOLDER
        self.folder_entry.config(state='normal')
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.selected_folder)
        self.folder_entry.config(state='readonly')

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    root.mainloop()
