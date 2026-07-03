import os
import threading
import concurrent.futures
import yt_dlp
import imageio_ffmpeg

def download_single_url(url, output_dir, ffmpeg_path, progress_callback, log_callback):
    """Hàm tải 1 URL duy nhất, được chạy song song"""
    def my_hook(d):
        if d['status'] == 'downloading':
            try:
                percent_str = d.get('_percent_str', '0.0%').strip()
                percent_str = percent_str.replace('\x1b[0;94m', '').replace('\x1b[0m', '')
                try:
                    percent = float(percent_str.replace('%', ''))
                except:
                    percent = 0.0
                if progress_callback:
                    # Gửi tiến trình kèm theo tên file hoặc url để UI biết (hiện tại tính chung)
                    progress_callback(url, percent / 100.0)
            except Exception as e:
                pass
        elif d['status'] == 'finished':
            if log_callback:
                log_callback(f"Download finished. Converting to MP3: {d.get('filename', 'Unknown')}")

    class MyLogger:
        def debug(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg):
            if log_callback:
                log_callback(f"Download error {url}: {msg}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'ignoreerrors': True,
        'nocheckcertificate': True,
        # Removed cookiesfrombrowser due to Chrome/Edge DPAPI encryption issues
        # === CÁC CÁCH LÁCH LUỒNG / TĂNG TỐC YOUTUBE ===
        # 1. Sử dụng client Android để tránh bị YouTube bóp băng thông (rất hiệu quả hiện nay)
        'extractor_args': {'youtube': ['player_client=android']},
        # 2. Bỏ qua việc tải ảnh thumbnail/sub để nhẹ hơn
        'writethumbnail': False,
        'writesubtitles': False,
        # 3. Tăng số block tải cùng lúc (đặc biệt hữu ích nếu mạng mạnh)
        'concurrent_fragment_downloads': 5,
        'http_chunk_size': 10485760, # Tải chunk 10MB
    }
    
    # Support cookies.txt if it exists in the same folder as the exe
    import sys
    try:
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    except:
        base_dir = os.getcwd()
        
    cookies_path = os.path.join(base_dir, 'cookies.txt')
    if os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        return False

def download_mp3_task(urls, output_dir, progress_callback=None, log_callback=None, finished_callback=None):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    # Sử dụng ThreadPool để tải nhiều link CÙNG MỘT LÚC (Tối đa 3 link song song)
    max_workers = min(3, len(urls)) 
    if log_callback:
        log_callback(f"Start downloading {len(urls)} links ({max_workers} parallel threads)...")
        
    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit các task
        futures = {executor.submit(download_single_url, url, output_dir, ffmpeg_path, progress_callback, log_callback): url for url in urls}
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success_count += 1

    if finished_callback:
        if success_count == len(urls):
            finished_callback(True, f"Successfully downloaded {success_count}/{len(urls)} items!")
        elif success_count > 0:
            finished_callback(True, f"Successfully downloaded {success_count}/{len(urls)} items. Some links failed.")
        else:
            finished_callback(False, "Failed to download all links.")

def start_download_thread(urls, output_dir, progress_callback, log_callback, finished_callback):
    """Khởi chạy download trên thread riêng để không block UI"""
    thread = threading.Thread(
        target=download_mp3_task, 
        args=(urls, output_dir, progress_callback, log_callback, finished_callback),
        daemon=True
    )
    thread.start()
