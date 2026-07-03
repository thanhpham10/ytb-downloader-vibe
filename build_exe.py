import PyInstaller.__main__
import customtkinter
import os

customtkinter_path = os.path.dirname(customtkinter.__file__)

PyInstaller.__main__.run([
    'main.py',
    '--name=YtMp3Downloader',
    '--onefile',         # Đóng gói thành 1 file duy nhất để dễ chia sẻ
    '--windowed',        # Ẩn cửa sổ console đen khi chạy
    '--icon=YouTub.ico', # Thiết lập icon cho file .exe
    f'--add-data={customtkinter_path};customtkinter/', # Gộp thư viện CustomTkinter
    '--add-data=YouTub.ico;.',                         # Gộp file icon vào thư mục tạm của ứng dụng
    '--collect-all=imageio_ffmpeg',                    # Gộp thư viện ffmpeg
    '--distpath=abs',    # Xuất file exe ra folder 'abs' theo yêu cầu
    '--noconfirm',       # Ghi đè thư mục cũ nếu có
])
