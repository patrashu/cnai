from ultralytics import YOLO

# Load a model
model = YOLO('yolov8n.pt')  # load an official detection model

# Track with the model
# results = model.track(source="https://youtu.be/Zgi9g1ksQHc", show=True) 

model.track(source="C:\\Users\\syu\\Documents\\hnv\\cnai\\object_tracking\\assets\\ch02_cut.mp4", show=True, tracker="bytetrack.yaml") 