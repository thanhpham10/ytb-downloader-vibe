import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import sys
from downloader import start_download_thread

# ========== Hàm tìm đường dẫn icon khi chạy từ .exe hoặc .py ==========
def resource_path(relative_path):
    """Tìm đường dẫn tuyệt đối cho file tài nguyên, tương thích cả PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller tạm thời giải nén vào đây
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ========== Cấu hình giao diện ==========
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class YtMp3DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("APP CREATED BY THANH - DO NOT COPYRIGHT")
        self.geometry("780x700")
        self.minsize(600, 550)

        # Đặt icon cho cửa sổ
        icon_path = resource_path("YouTub.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Trạng thái
        self.download_folder = os.path.expanduser("~/Downloads")
        self.is_downloading = False
        self.log_history = []

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # URL input
        self.grid_rowconfigure(5, weight=1)  # Log box

        # ===== TIÊU ĐỀ =====
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="YTB downloader - Thanh",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0)

        ctk.CTkLabel(
            header_frame,
            text="YTB link, one link in one row",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).grid(row=1, column=0, pady=(2, 0))

        # ===== Ô NHẬP LINK =====
        ctk.CTkLabel(
            self,
            text="📋 Link YouTube:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).grid(row=1, column=0, padx=24, pady=(14, 2), sticky="w")

        self.urls_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13))
        self.urls_textbox.grid(row=2, column=0, padx=24, pady=(0, 8), sticky="nsew")
        self.urls_textbox.insert("end", "# Example:\n# https://www.youtube.com/watch?v=...\n# https://www.youtube.com/playlist?list=...")

        # ===== CHỌN THƯ MỤC =====
        folder_frame = ctk.CTkFrame(self)
        folder_frame.grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        folder_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(folder_frame, text="📁SAVE:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, padx=12, pady=10
        )

        self.folder_entry = ctk.CTkEntry(folder_frame, state="disabled", font=ctk.CTkFont(size=12))
        self.folder_entry.grid(row=0, column=1, padx=8, pady=10, sticky="ew")
        self.folder_entry.configure(state="normal")
        self.folder_entry.insert(0, self.download_folder)
        self.folder_entry.configure(state="disabled")

        ctk.CTkButton(
            folder_frame,
            text="Select Folder",
            width=130,
            command=self._select_folder,
        ).grid(row=0, column=2, padx=12, pady=10)

        # ===== THANH TIẾN TRÌNH & NÚT TẢI =====
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.grid(row=4, column=0, padx=24, pady=4, sticky="ew")
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(ctrl_frame, height=16, corner_radius=8)
        self.progress_bar.grid(row=0, column=0, columnspan=2, padx=0, pady=(4, 6), sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            ctrl_frame, text="OK", text_color="green", font=ctk.CTkFont(size=12), anchor="w"
        )
        self.status_label.grid(row=1, column=0, sticky="w")

        self.download_btn = ctk.CTkButton(
            ctrl_frame,
            text="Let's go",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            corner_radius=10,
            command=self._start_download,
        )
        self.download_btn.grid(row=2, column=0, columnspan=2, pady=(10, 4), sticky="ew")

        # ===== HỘP ĐEN LOG =====
        ctk.CTkLabel(
            self,
            anchor="w",
        ).grid(row=5, column=0, padx=24, pady=(10, 2), sticky="nw")

        log_frame = ctk.CTkFrame(self, corner_radius=10)
        log_frame.grid(row=5, column=0, padx=24, pady=(28, 16), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0d0d0d",
            text_color="#ff00ff",
            state="disabled",
            corner_radius=8,
        )
        self.log_textbox.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

    # ==================== CALLBACKS ====================

    def _select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.folder_entry.configure(state="disabled")
            self._log_to_box(f"Save directory: {folder}")

    def _log_to_box(self, msg):
        """Ghi 1 dòng vào hộp đen log"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{msg}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        self.log_history.append(msg)
        if len(self.log_history) > 50:
            self.log_history.pop(0)

    def log_message(self, msg):
        """Callback từ thread tải — chạy an toàn trên main thread"""
        self.after(0, lambda: self._log_to_box(msg))
        self.after(0, lambda: self.status_label.configure(text=msg[:80]))

    def update_progress(self, url, percent):
        """Cập nhật tiến trình từng URL và tổng thể"""
        if not hasattr(self, 'download_progress'):
            return
        self.download_progress[url] = percent
        overall = sum(self.download_progress.values()) / self.total_urls

        def _ui():
            self.progress_bar.set(overall)
            self.status_label.configure(
                text=f"ALL: {int(overall * 100)}%  |  {sum(v >= 1.0 for v in self.download_progress.values())}/{self.total_urls} items completed"
            )
            # Cập nhật toàn bộ hộp đen
            lines = ["=== download misson ==="]
            for u, p in self.download_progress.items():
                bar = "█" * int(p * 20) + "░" * (20 - int(p * 20))
                short_url = u[-55:] if len(u) > 55 else u
                lines.append(f"[{int(p*100):>3}%] {bar}  {short_url}")
            if self.log_history:
                lines.append("")
                lines.append("=== LOGS ===")
                lines.extend(self.log_history[-10:])  # 10 dòng log gần nhất

            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("end", "\n".join(lines))
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

        self.after(0, _ui)

    def on_download_finished(self, success, msg):
        self.is_downloading = False

        def _ui():
            self.download_btn.configure(state="normal", text="LET'S START")
            self.progress_bar.set(1.0 if success else 0)
            color = "#2ecc71" if success else "#e74c3c"
            self.status_label.configure(text=msg, text_color=color)
            self._log_to_box(f"\n{'✅ FINISHED' if success else '❌ FAILED'}: {msg}\n")
            if success:
                tk.messagebox.showinfo("OK", f"{msg}\nSave at: {self.download_folder}")
            else:
                tk.messagebox.showerror("ERRORS", msg)

        self.after(0, _ui)

    def _start_download(self):
        if self.is_downloading:
            return

        raw = self.urls_textbox.get("1.0", "end-1c").strip()
        urls = [
            line.strip()
            for line in raw.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        if not urls:
            tk.messagebox.showwarning("ERRORS", "Please paste at least one YouTube link!!!")
            return

        self.is_downloading = True
        self.download_progress = {u: 0.0 for u in urls}
        self.total_urls = len(urls)
        self.log_history.clear()

        self.download_btn.configure(state="disabled", text="⏳  Downloading...")
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Start download {len(urls)} ...", text_color=("gray70", "gray70"))

        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self._log_to_box(f"App created by Thanh Pham - do not copyright")

        start_download_thread(
            urls=urls,
            output_dir=self.download_folder,
            progress_callback=self.update_progress,
            log_callback=self.log_message,
            finished_callback=self.on_download_finished,
        )


if __name__ == "__main__":
    app = YtMp3DownloaderApp()
    app.mainloop()
