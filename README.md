# 2023-1 산학연계 SW캡스톤 디자인 프로젝트- 인공지능 기반 방문자 관리 시스템

![image](https://github.com/patrashu/cnai/assets/49676680/47ed0b55-c2dd-4a5d-8057-89b64be53e14)

- 삼육대학교 산학연계 SW캡스톤 디자인 프로젝트 - 인공지능 기반 방문자 관리 시스템
- CNAI 기업과 멘토링 [기업  사이트](https://cnai.ai/home)
- 개발 기간 : 2023/03/10 ~ 2023/06/21
  
## 프로젝트 소개

- 매장 내 CCTV를 기준으로 실시간 방문객을 분석하여 성별, 연령대, 매장 앞 외부 유동인구 등의 정보 수집을 목표
- 기존 AI 기반 방문객 시스템을 개선하여 문제점을 해결하고 동선 분석 등의 Task를 Computer Vision으로 해결해보고자 함
- 실내 방문객의 성별 및 연령대 예측을 통해 마케팅 활용

## 데이터셋 소개

- 실제 매장의 24시간 CCTV 4대의 영상(1540x1240)을 사용
- [한국인 재식별 데이터셋](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=realm&dataSetSn=84) : 성별 & 나이 인식에 사용

## Get Started

```
conda create -n cnai python=3.9 -y
conda activate cnai
pip install -r requirements.txt
conda install pytorch torchvision pytorch-cuda=11.7 -c pytorch -c nvidia -y
python main.py
```

## 주요 기능

![Screenshot from 2023-06-19 13-23-43](https://github.com/patrashu/cnai/assets/49676680/b7348373-3aaa-4d55-82f2-88739ebe479b)
![Screenshot from 2023-06-19 14-56-34](https://github.com/patrashu/cnai/assets/49676680/5fb0e765-34cc-4eb1-8730-619254b33902)

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
