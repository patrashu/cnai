from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QImage

class AllSignals(QObject):
    stacked_sidebar_status = Signal(str)
    stacked_status = Signal(str)

    streaming_video1 = Signal(QImage)
    streaming_video2 = Signal(QImage)
    streaming_video3 = Signal(QImage)
    streaming_cam = Signal(QImage)
    streaming_gender = Signal(QImage)
    # minimap = Signal(QImage)

    def __init__(self) -> None:
        super().__init__()


class VisSignals(QObject):
    TotalFrame = Signal(int)
    CurrentFrame = Signal(int)
    streaming_vis = Signal(QImage)
    Complete = Signal(bool)
    CenterPt = Signal(list)
    ObjectId = Signal(str)


all_signals = AllSignals()
vis_signals = VisSignals()