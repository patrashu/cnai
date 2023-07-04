# 2023-1 산학연계 SW캡스톤 디자인 프로젝트- 인공지능 기반 방문자 관리 시스템

## 프로젝트 소개

- 매장 내 CCTV를 기준으로 실시간 방문객을 분석하여 성별, 연령대, 매장 앞 외부 유동인구 등의 정보 수집을 목표
- 기존 AI 기반 방문객 시스템을 개선하여 문제점을 해결하고 동선 분석 등의 Task를 Computer Vision으로 해결해보고자 함
- 실내 방문객의 성별 및 연령대 예측을 통해 마케팅 활용

## 데이터셋 소개

- 실제 매장의 24시간 CCTV 4대의 영상(1540x1240)을 사용


## Get Started

```
conda create -n cnai python=3.9 -y
conda activate cnai
pip install -r requirements.txt
conda install pytorch torchvision pytorch-cuda=11.7 -c pytorch -c nvidia -y
python main.py
```

## 주요 기능

- Face Detection
- Age & Gender Classification
- Object Tracking
- Visitor Visualization

## 기술 스택

- Python
- PyTorch
- PyTorch-Lightning
- PySide6
- OpenCV
- Matplotlib
- Wandb
