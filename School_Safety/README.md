# [공공/XAI] 학교안전사고 데이터 분석 및 활용 경진 대회

예선 결과 : 5위/참가 인원 모름

## 목차

### 1️⃣ 개요
### 2️⃣ 데이터
### 3️⃣ 전처리
### 4️⃣ EDA
### 5️⃣ 시도한 것들
### 6️⃣ 모델링
### 7️⃣ 결과
### 📌 정리 및 배운점
<br>

## 1️⃣ 개요

- **기간 및 인원**: 2025.06.15-2024.07.18 / 개인
- **문제 정의**:
  - **필요성**:
    2023학년도 학교안전공제중앙회 통계에 따르면 학교안전사고 건수는 총 193,177건으로, 전년 대비 43,838건(29.4%) 증가한 것으로 나타남. 이는 저출산으로 인한 학생 수 감소 추세와는 반대되는 현상으로(출처: 교육언론 [창]) 학생 1인당 사고 발생 위험이 상대적으로 높아지고 있음을 시사함. <br> 이와 함께 교사, 학부모 간 갈등, 교권 침해 논란, 불분명한 배상 책임 문제 등 단순한 사고를 넘어 사회적 갈등과 불안 요소로 이어지고 있는 상황임(EBS 뉵, 2024; 교육희망, 2021; 한국교총, 2003). <br>
  - **연구 목적**:
    교육기관별 학교안전사고 데이터를 정량 분석하여, 기관 특성과 연령에 따른 주요 사고 원인을 규명하는 것을 목표로 하며, 분석 결과를 실질적인 예방법으로 재구성하고, 이를 웹툰 콘텐츠로 시각화하여 학교 안전 문화 확산, 사고 예방, 교육 주체 간 신뢰 회복에 기여하고자 함. <br>
  
- **주요 역할**:
  - EDA 및 전처리
  - 예측 모델링
  - 결과 해석
<br>

## 2️⃣ 데이터

- **데이터**
  - 학교안전공제중앙회 제공 데이터
  - 2020년~2025년 안전사고 데이터
    - 공통으로 지역, 교육청, 학교급, 사고자구분, 학년, 시간, 장소, 부위, 형태, 활동 데이터가 존재
    - 보상 데이터는 지급된 급여의 종류와 급여액이 포함되어 있음.
  - 보상 데이터: 245214 rows x 19 columns
  - 사고 데이터: 689253 rows x 15 columns
<br>

## 3️⃣ 전처리

- **요약**
  - na행 제거
  - 불필요 feature 제거
  - 급여 변수 통일
 
- **1. na 행 제거**
  - 학교안전사고 중 사고자 학년에 na 포함.
  - 이는 교직원의 사고로, 분석 목적에 맞게 학생 데이터만을 남기려 했고, 총 1632행 제거

<img width="190" height="316" alt="image" src="https://github.com/user-attachments/assets/fcff10c2-bcb2-484f-9e36-49aef09891de" />


- **2. 불필요한 feautre 제거**
  - 안전교육홍보 목적: 일반화를 위해 지역을 남기고 교육청은 제거
  - 사고발생일에서 월만 남김: 년도와 일에 비해 월은 방학 여부, 계절 정보를 담고 있음
  - 사고발생 시각의 분석을 위해 ':' 제거
  - 학교급(초/중/고 등)과 사고자학년(1학년, 2학년,...,6학년) 변수를 합쳐 사용

- **3. 급여 변수**
  - 유형별로 나뉘어져 있던 급여 변수들을 '보상급여'라는 하나의 변수로 통일화
  - 급여 유형별로 금액의 기본 크기 차이가 존재하기 때문에, 이는 논리적으로 맞는 접근법이라고 판단

<img width="282" height="452" alt="image" src="https://github.com/user-attachments/assets/9363e50d-be3c-494e-b3d2-3ecc28ad8d4e" />
<img width="85" height="546" alt="image" src="https://github.com/user-attachments/assets/83e40c55-d848-40ab-b593-d62a20ae43bb" />

## 4️⃣ EDA

- **4.1 기본 기술 통계**
  - 변수별 unique 및 개수 확인
  - 변수별 plot 시각화
 
<img width="857" height="686" alt="image" src="https://github.com/user-attachments/assets/aff48847-ba15-4bab-9483-c6db45d0ca8f" />
<img width="620" height="419" alt="image" src="https://github.com/user-attachments/assets/169e8788-5b41-4494-8ebf-d04f87e9b9ed" />
<img width="850" height="744" alt="image" src="https://github.com/user-attachments/assets/3c236320-587d-4125-8d92-a8f44ef86c78" />

- 지역: 인구 수 자체가 많은 서울, 경기권이 다수
- 학교급_사고자학년: 초등학교 고학년~중학교까지 인원이 많고 고등학교부터 약간 줄어듦
- 성별: 비교적 더 활동적인 남자가 약 2배가 더 많음

- **외 변수들은 범주가 많아 따로 시각화하여 확인**

- **사고시간**
  - <img width="844" height="556" alt="image" src="https://github.com/user-attachments/assets/c009f671-6770-4b96-bfe0-df26a1ac874c" />
  - 활동량이 많은 체육시간이 1/3차지. 외에 식사시간(계단과 뛰어다니는 행동), 쉬는시간(수업시간보다 활동이 많은)을 포함하면 65.2%를 차지
 
- **사고장소**
  - <img width="851" height="565" alt="image" src="https://github.com/user-attachments/assets/cc5e3714-50d6-4054-a7ac-a56a5882259f" />
  - 사고시간 분석과 유사하게 체육시간에 쓰이는 강당, 운동장 그리고 쉬는시간, 식사시간에 포함되는 교실, 계단 및 복도가 큼

- **사고형태**
  - <img width="849" height="559" alt="image" src="https://github.com/user-attachments/assets/bd317d88-da42-4c97-a4de-83e3185c9c1a" />
  - 사고형태는 대부분 넘어짐, 부딪힘.

- **사고당시활동**
  - <img width="851" height="569" alt="image" src="https://github.com/user-attachments/assets/985dad6f-791f-498e-86b2-fcb910fd2fc4" />
  - 사고당시활동 흔한 일들인 걷기/뛰기/오르내리기와 장난, 축구/농구/피구와 같은 다칠 가능성이 높은 체육활동들
 
- **사고부위**
  - <img width="846" height="556" alt="image" src="https://github.com/user-attachments/assets/d8e94ade-e18f-4365-9f08-1dbec5169348" />
  - 대부분 넘어졌을 때 쉽게 다칠 수 있고, 공에 부딪혀 다칠 수 있는 손가락, 발목, 무릎 눈, 손목 등 많이 사용하는 손과 발이 큰 비중 차지
 
- **보상급여**
  - <img width="854" height="561" alt="image" src="https://github.com/user-attachments/assets/5e1f7cff-7bcf-48a2-9292-cde005ade4b3" />
  - <img width="418" height="94" alt="image" src="https://github.com/user-attachments/assets/bc782d17-0fa1-4368-b36c-ab1b21c7ea0d" />

  - 일정 금액 이상(0.6 * 1e9)은 특이 케이스로 빈도가 크지 않다.
  - 보상급여가 2천 만원 미만인 데이터가 약 99& 차지
 
- **4.2 상관관계 확인**

## 5️⃣ 시도한 것들

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

## 6️⃣ 모델링

- GBM, CATBoost, RF, Lightgbm, XGBoost 선정(AutoML 기준)
- 불량 제품의 유통을 막는 것이 중요하기 때문에(사후 대응 비용 증가, 고객 만족도 저하) softvoting을 통해 엄격한 모델을 생성

![image](https://github.com/user-attachments/assets/ff9d12d5-5250-4349-a033-6d87c4353d18)

![image](https://github.com/user-attachments/assets/504f3dc3-3a61-46e3-92a2-844a3ba14955)
<br>

## 7️⃣ 결과

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
