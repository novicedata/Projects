# [공공/XAI] 학교안전사고 데이터 분석 및 활용 경진 대회

예선 결과 : 1차 심사 통과(진행중)

## 목차

### 1️⃣ 개요
### 2️⃣ 데이터
### 3️⃣ EDA 및 전처리
### 4️⃣ 시도한 것들
### 5️⃣ 모델링
### 6️⃣ 결과
### 📌 정리 및 배운점
<br>

## 1️⃣ 개요

- **기간 및 인원**: 2025.06.15-2024.07.18 / 개인
- **문제 정의**:
  - **필요성**:
    2023학년도 학교안전공제중앙회 통계에 따르면 학교안전사고 건수는 총 193,177건으로, 전년 대비 43,838건(29.4%) 증가한 것으로 나타남. 이는 저출산으로 인한 학생 수 감소 추세와는 반대되는 현상으로(출처: 교육언론 [창]) 학생 1인당 사고 발생 위험이 상대적으로 높아지고 있음을 시사함. <br> 이와 함께 교사, 학부모 간 갈등, 교권 침해 논란, 불분명한 배상 책임 문제 등 단순한 사고를 넘어 사회적 갈등과 불안 요소로 이어지고 있는 상황임(EBS 뉵, 2024; 교육희망, 2021; 한국교총, 2003).
<br>
  - **연구 목적**:
    교육기관별 학교안전사고 데이터를 정량 분석하여, 기관 특성과 연령에 따른 주요 사고 원인을 규명하는 것을 목표로 하며, 분석 결과를 실질적인 예방법으로 재구성하고, 이를 웹툰 콘텐츠로 시각화하여 학교 안전 문화 확산, 사고 예방, 교육 주체 간 신뢰 회복에 기여하고자 함.
  - ****
- **주요 역할**:
  - EDA 및 전처리
  - ML 모델링 및 Voting 도입
<br>

## 2️⃣ 데이터

- **데이터**
  - 주관 기관의 디스플레이 공정 데이터로 4가지 공정 단계로 이루어짐(AutoClave, Dam, Fill1, Fill2)
  - Trian data: 40,506 rows / Test data: 17,361 rows / Features: 464 columns
  - Imbalanced data: 38,156(Normal), 2,350(AbNormal)
  - 이상 공개 불가
- **도메인 지식**
  - Dam(레진도포&반경화) -> AutoClave(탈포) -> Fill1(도포) -> Fill2(경화)
  - 합착, 완전 경화 공정에 대한 데이터셋이 주어지지 않아 생산 과정에서 일어나는 모든 불량 유형을 예측할 수 없음.
  - (https://youtu.be/JOuV4HuKQds?si=-Emi4eiEegSqQvWI, https://youtu.be/feNewpVvC5M?si=6nKSvJ8f6jW_CXUd)
<br>

## 3️⃣ EDA 및 전처리

- **요약**
  - 한 열씩 밀린 데이터 조정
  - 같은 unique를 갖는 열들 1개만 남기고 삭제
  - Categoricla columns 인코딩
 
- **1. 밀린 열 조정**
  - 아래와 같이 특정 feature 부터 한 열씩 밀려 데이터가 생성됨을 확인
  - 이를 조정하는 과정에서 생기는 결측 행은 삭제 or 다수요인으로 포함

![image](https://github.com/user-attachments/assets/5e63f2ff-3d71-4c8e-b787-c517882b3f3b)

- **2. 각 feature가 설명하는 바와 범위 정리**
  - 각 feature가 뜻하는 의미를 도메인 지식 학습 후 정리
  - 연속 or 범주형, 범위, 오류항 확인


![image](https://github.com/user-attachments/assets/a655a745-def5-4e46-b393-781047b0077d)
---
![image](https://github.com/user-attachments/assets/948a68fe-6b60-4b0c-b3c2-faddc0f52f35)

- **3. 각 공정별 feature의 plot 및 상관 확인**
  - 확인 결과 이진형 데이터의 경우 unique별 example 개수가 같은 변수들이 있음을 확인
  - 상관을 보았을 때에도 1.00이 됨을 확인
  - 이러한 변수들은 모델링 과정에서 한개만 있으면 되기에 삭제

![image](https://github.com/user-attachments/assets/3f720a80-f94b-4d6b-8753-24dc5f2435b2)
![image](https://github.com/user-attachments/assets/bc8ab7d1-e1d1-4ddb-91fc-c95fd8a10cb0)


## 4️⃣ 시도한 것들

- **코드북 분실로 정확한 수치 변화 소실**
- **유의한 변화가 없던 시도**
  - 다중공선성 처리: 앞서 완전 상관인 변수들을 제거하고 문제될 것 없음
  - 불균형 데이터 처리: 언더샘플링, 오버샘플링 모두 큰 효과를 보지 못함
  - PCA: PCA보다는 파생변수 생성이 더 큰 효과를 낳음
 
- **유의한 변화가 있던 시도**
  - 파생변수 생성: 도메인 지식 기반 공정 단계의 유관성이 큰 경우 파생변수화
  - Feature importance 기반 변수 선택: feature importance를 근거로 Top5 변수로 모델
  - Softvoing: 총 5개의 모델(GBM, CATBoost, RF, Lightgbm, XGBoost)을 soft voting 처리[AutoML 순위 Top5]
  - Threshold 변경: 불균형 데이터이기 때문에 분류 기준을 0.5가 아닌 train 기준 threshold로 변경
<br>

## 5️⃣ 모델링

- GBM, CATBoost, RF, Lightgbm, XGBoost 선정(AutoML 기준)
- 불량 제품의 유통을 막는 것이 중요하기 때문에(사후 대응 비용 증가, 고객 만족도 저하) softvoting을 통해 엄격한 모델을 생성

![image](https://github.com/user-attachments/assets/ff9d12d5-5250-4349-a033-6d87c4353d18)

![image](https://github.com/user-attachments/assets/504f3dc3-3a61-46e3-92a2-844a3ba14955)
<br>

## 6️⃣ 결과

- Best Threshold: 0.836, Best F1 Score: 0.2210 (Train 기준)
- 최종 결과
  - Best F1 Score: 0.215569
  - 56위/740
<br>

## 📌 정리 및 배운점

- **대중적인 ML 기법에만 집착**
  - 본선 진출자들의 코드를 분석했을 때 일반적인 ML 보다는 이상치 탐지에 유리한 모델들을 사용한 것을 확인
  - 너무 아는 모델만을 활용하려고 한 점이 아쉽다.(추가적인 공부를 했으면 좋았을 것)
 
- **Voting만을 한 점**
  - Voting을 제외한 스태킹, 평균화 방법 등 앙상블 기법이 많은데 사용하지 못한 점이 아쉽다

 
- **배운점**
  - **pycaret 기반 AutoML의 사용**
    - for문을 통한 ML들을 사용할 경우 각 ML 마다의 파라미터를 따로 조정해줘야함(같은 파라미터라도 명이 다름)
    - AutoML을 통해 효율적이게 어떤 모델이 유리한지 파악할 수 있었고 이들의 파라미터를 세부조정함으로써 시간 단축이 가능했다
      
  - **Shapley value, Forward Feature Importance에 대한 적용**
    - 단순 이론만 알고 있었지만 이번 기회로 실제 중요한 요인들이 왜 중요할까? 라는 생각을 할 수 있게 되었음.
      
  - **실제 데이터를 통한 프로젝트**
    - 실제 도메인 데이터의 이해가 매우 중요하다는 것을 배움
    - feature가 무엇을 뜻하느냐를 확인해야 분석 또한 효율적이고 목표 지향적으로 가능하다는 점
