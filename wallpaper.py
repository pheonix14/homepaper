import os
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

class WallpaperBase(QWidget):
    """
    Base class for all wallpapers.
    """
    def __init__(self):
        super().__init__()
        # Remove window borders and set it to full screen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

class VideoWallpaper(WallpaperBase):
    """
    A wallpaper that plays a video file on loop.
    """
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Mute audio by default for wallpapers
        self.audio_output.setVolume(0.0)

        self.media_player.setSource(QUrl.fromLocalFile(os.path.abspath(video_path)))
        self.media_player.setLoops(QMediaPlayer.Infinite)

    def play(self):
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()

class WebWallpaper(WallpaperBase):
    """
    A wallpaper that renders an HTML page or URL.
    """
    def __init__(self, url_or_path):
        super().__init__()
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
        except ImportError:
            print("PySide6-WebEngine is not installed. WebWallpapers will not work.")
            return

        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)
        
        if os.path.exists(url_or_path):
            self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(url_or_path)))
        else:
            self.web_view.setUrl(QUrl(url_or_path))

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass
