from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QStackedLayout, QFrame
)

from .viewer_video import StreamingVideo 
from .viewer_cam import StreamingCam 
from .viewer_vis import Visualization
from ..signals import all_signals


class StackedViewer(QFrame):
    def __init__(self) -> None:
        super().__init__()
        all_signals.stacked_sidebar_status.connect(self.setCurrentWidget)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumHeight(1080)
        self.setMaximumWidth(1900)
        
        self.main_layout = QStackedLayout()
        self.viewer_video = StreamingVideo()
        self.viewer_cam = StreamingCam()
        self.viewer_vis = Visualization()
        
        self.main_layout.addWidget(self.viewer_video)
        self.main_layout.addWidget(self.viewer_vis)
        self.main_layout.addWidget(self.viewer_cam)

        # 현재 index
        self.main_layout.setCurrentIndex(0)
        self.setLayout(self.main_layout)

    @Slot(str)
    def setCurrentWidget(self, value):
        if value == "camera":
            self.main_layout.setCurrentWidget(self.viewer_cam)
        elif value == "visualization":
            self.main_layout.setCurrentWidget(self.viewer_vis)
        else:
            self.main_layout.setCurrentWidget(self.viewer_video)