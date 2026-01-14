# [공공/XAI] 학교안전사고 데이터 분석 및 활용 경진 대회

최종 결과 : 5위/참가 인원 모름

## 목차

#### 1️⃣ 개요
#### 2️⃣ 데이터
#### 3️⃣ 전처리
#### 4️⃣ EDA
#### 5️⃣ 분포 분석
#### 6️⃣ 모델링
#### 7️⃣ 결과
#### 📌 결론
#### 📌 정리 및 배운점
<br>

## 1️⃣ 개요

- **기간 및 인원**: 2025.06.15-2024.07.18 / 개인
- **문제 정의**:
  - **필요성**:
    - 2023학년도 학교안전공제중앙회 통계에 따르면 학교안전사고 건수는 총 193,177건으로, 전년 대비 43,838건(29.4%) 증가한 것으로 나타남.
    - 이는 저출산으로 인한 학생 수 감소 추세와는 반대되는 현상으로(출처: 교육언론 [창]) 학생 1인당 사고 발생 위험이 상대적으로 높아지고 있음을 시사함.
    - 이와 함께 교사, 학부모 간 갈등, 교권 침해 논란, 불분명한 배상 책임 문제 등 단순한 사고를 넘어 사회적 갈등과 불안 요소로 이어지고 있는 상황임(EBS 뉵, 2024; 교육희망, 2021; 한국교총, 2003). <br>
  - **연구 목적**:
    - 교육기관별 학교안전사고 데이터를 정량 분석하여, 기관 특성과 연령에 따른 주요 사고 원인을 규명하는 것을 목표
    - 분석 결과를 실질적인 예방법으로 재구성하고, 이를 웹툰 콘텐츠로 시각화하여 학교 안전 문화 확산, 사고 예방, 교육 주체 간 신뢰 회복에 기여하고자 함. <br>
  
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
  - '사고자 구분' 항목은 너무 편향되어 있어 상관을 보기 어렵다고 판단하여 상관 분석에서 제거
  - <img width="844" height="778" alt="image" src="https://github.com/user-attachments/assets/8d38f9e5-8da4-45dc-b8ca-91d121792ae9" />

  - 사고자 학년, 학교급, 추정나이간 상관은 추정나이 자체가 이들의 파생 변수라 높은 상관은 당연한 결과
  - 사고 시간, 사고 장소, 사고 형태, 사고 당시 활동, 사고 부위: 학교 특성상 정해진 시간에 정해진 장소에 있을 가능성이 높고 장소에 따라 당시에 무엇을 했는지, 어떤 사고인지, 그래서 어딜 다쳤는지 유추할 수 있음.
  - **궁금한 것은 학교급/사고자학년/추정나이라는 수준 변수와 사고시간/장소/부위/당시활동/형태와 왜 상관이 높을까?라는 의문**


## 5️⃣ 분포 분석

- **추정나이가 아닌 학교급과 학년에 따라 구분하여 분석**
- **사고자학년**
  - <img width="848" height="565" alt="image" src="https://github.com/user-attachments/assets/642d4ee7-25dd-4396-8580-ce5dd7e0bbfb" />
  - <img width="857" height="559" alt="image" src="https://github.com/user-attachments/assets/1dd38a37-842f-4998-b8f1-0bd5fc3e6ffa" />
  - <img width="853" height="561" alt="image" src="https://github.com/user-attachments/assets/fe890888-6ec3-4216-bd96-85aacf227cac" />
  - <img width="844" height="560" alt="image" src="https://github.com/user-attachments/assets/7b20a890-6597-401a-81fe-1724ca5f3600" />
  - <img width="855" height="572" alt="image" src="https://github.com/user-attachments/assets/76e1df62-cd64-4753-9fcb-d7f677c87495" />

- 사고자학년의 경우 유치원생을 제외하고는 비슷한 분포를 확인할 수 있음(추정)

- **학교급**
  - <img width="849" height="557" alt="image" src="https://github.com/user-attachments/assets/157c369e-30b4-4f82-aaf2-6eb130118090" />
  - <img width="843" height="560" alt="image" src="https://github.com/user-attachments/assets/1ada437a-8d60-4e00-ad47-750dbb71bae7" />
  - <img width="849" height="563" alt="image" src="https://github.com/user-attachments/assets/baf7de6f-59e4-4428-a062-f74eda859cf2" />
  - <img width="854" height="558" alt="image" src="https://github.com/user-attachments/assets/e2c6606e-5493-49ec-9b9d-c03ca147fd95" />
  - <img width="845" height="562" alt="image" src="https://github.com/user-attachments/assets/91c1a5a2-9236-4a75-8876-cb90e833d1d0" />

- 학교급 또한 유치원생을 제외하고 모두 비슷한 분포를 보이지만 결국 사고형태는 넘어짐이 제일큼

- **종합**
  - 상관 결과 일반적으로 상관이 있을 것이라는 요인들은 실제로 상관이 존재
  - 외 학년, 학교급, 추정 나이의 경우 범주형 변수의 특성 상 상관이 높게 생긴 것으로 확인
    - 단, 실제로 학교급/사고자학년에서 유치원생의 요인이 크게 다르다는 것은 사실
<br>

## 6️⃣ 모델링

- Label을 유치원생과 초/중/고로 나누어 이진 분류를 진행
  - 이진 분류를 통해 이 들간의 사고 유형과 관계의 차이를 확인하고자 함.
  - 분류시 모델의 해석 및 설명력을 위해 XAI 중 하나인 ShapeValue를 사용.
 
- 분류 모델을 확인하기 위해 pycaret기반 AutoML을 사용하였고, 여러 성능 지표에서 1위를 달성했던 XGBoost를 사용.

<img width="800" height="305" alt="image" src="https://github.com/user-attachments/assets/1cf33134-ccde-4e61-991c-9a57dfd89707" />
<img width="723" height="182" alt="image" src="https://github.com/user-attachments/assets/6a85ce50-a014-4287-b74f-f30789adcf8c" />
<br>

## 7️⃣ 결과

- SHAP value
  - <img width="247" height="236" alt="image" src="https://github.com/user-attachments/assets/ec808a77-9fe9-44a4-bc82-e8834e11cfde" />
  - 사고당시활동, 사고시간, 사고장소, 사고형태, 사고부위, 보상급여, 성별 순으로 중요도가 나열
  - 그 중에서도 사고당시활동, 사고시간, 사고장소, 사고형태가 높은 중요도를 보임
  - 높은 중요도를 보이는 4가지 간의 상관을 확인해보려고 한다.

- **해석 방법**
  - Y축의 위치
    - 해당 변수의 영향력을 나타내는 것
    - 0보다 클수록(위로 갈수록) 이 변수는 유치원으로 예측되게 만드는 변수
    - 0보다 작을수록(아래로 갈수록) 이 변수는 초중고로 예측되게 만드는 변수
   
  - 색깔
    - 다른 변수 하나와의 연관성
    - 빨간색부터 파란색까지 쭉 나열된 것
    - 예를 들어 사고장소와 상관을 본다면?
      - 빨간색: 예. 해당 사고당시활동은 사고 장소가 빨간색일 때 자주 발생
      - 파란색: 예. 해당 사고당시활동은 사고 장소가 파란색일 때 자주 발생

- **7.1 사고당시활동 vs 사고시간**
  - <img width="840" height="617" alt="image" src="https://github.com/user-attachments/assets/e112749d-3259-4f8f-b7b8-f6b8529977c0" />
  - 값이 높은 유치원을 보면(0값 기준)
    - 운전, 조작, 탑승과 같은 활동을 하는 현장학습, 하교 등의 상황에서 사고 발생
    - 장난, 놀이와 같은 활동을 하는 현장학습, 축제, 체육 활동 등의 상황에서 사고 발생
    - 걷기, 뛰기, 오르내리기의 경우 사고시간과 관계없이 유치원에서 자주 발생
    - 외에도 대부분의 활동에서 유치원에서 발생했다고 판단하기 더 쉽다
  - 값이 낮은 초중고를 보면
    - 농구, 뉴스포츠, 배구, 배드민턴, 피구, 테니스 등 대부분의 스포츠 활동에서 초중고 사고 발생이 높음
    - 활동 시간도 경기출전이나 체육대회, 자율활동 등 여러 시간대에서 골고루 발생
   
- **7.2 사고당시활동 vs 사고장소**
  - <img width="837" height="610" alt="image" src="https://github.com/user-attachments/assets/243436ad-2423-4911-bd90-41a6e3941273" />
  - 초중고는 주로 체육/구기활동(축구, 배드민턴, 농구 등)을 하며 사고가 많이 발생
    - 구기활동 특성에 맞게 주로 사고는 야외(체육관, 공원, 차도 등)에서 많이 발생
  - 그러나 유치원은 초중고와 달리 기타(일상, 씻기, 장난 등) 활동에서 사고가 많이 발생
    - 이에 따라 사고 장소 역시 실내(화장실, 현관, 교실 등)에서 많이 발생
   
- **7.3 사고당시활동 vs 사고형태**
  - <img width="839" height="609" alt="image" src="https://github.com/user-attachments/assets/3efc6944-b458-4bd6-97c9-82906157fbf9" />
  - 사고당시활동과 사고형태간의 관계는 크게 유관해보이지 않는다.
    - 점들의 색상이 어느쪽을 쏠리지 않고 혼합
   
- **7.4 사고시간 vs 사고장소**
  - <img width="836" height="620" alt="image" src="https://github.com/user-attachments/assets/89e93dba-afab-49fa-879c-98b2c76658c5" />
  - 초중고
    - 초중고의 사고시간은 다분포가 아닌 특정변수(특정 시간)들에 몰려있다.
    - 수련활동, 봉사활동, 경기출전 등으로 유치원 학생들이 하기 힘든 활동
    - or 식사시간, 쉬는 시간 등 선생님들이 케어하기 어려운 시간대에 발생
  - 유치원
    - (유치원)특성화활동을 제외하고(유치원에서만 하니까) 신체활동, 게임, 자율활동, 실외활동, 언어활동, 요리활동, 기타활동 시간 등 다양하게 분포되어 있다.
  - 주목할 점이라면 교육활동시간, 돌봄교실, 언어활동, 음악미술, 이론 수업 등 정적인 시간보다는 위에서 언급한 동적인 시간대에 더 유치원에서 발생한 사고라고 판단할 가능성이 높다.
 
- **7.5 사고시간 vs 사고형태**
  - <img width="832" height="613" alt="image" src="https://github.com/user-attachments/assets/5be70902-b6ad-459d-9ed0-0f50f72faece" />
  - 사고형태의 경우 사고당시활동과 다르게 사고시간에서는 약간의 관련이 있는 것으로 보인다
  - 같은 사고시간이더라도 유치원에 가까울수록 물집 접촉이나 열에의한 사고가 많다
  - 반면 초중고에 가까울수록 부딪히거나 떨어지거나 등 활동중에 다치는 사고가 많다

- **7.6 사고장소 vs 사고형태**
  - <img width="836" height="612" alt="image" src="https://github.com/user-attachments/assets/e0464e82-8c00-4acf-8833-f30518bca3e4" />
  - 장소와 형태간의 연관성은 크게 있어 보이지 않는다
  - 차이라면 유치원은 가정, 놀이터, 급식실, 화장실 등에서 많이 발생하고
  - 초중고는 과학실, 운동장, 교통구역 등에서 많이 발생한다.

## 📌 결론

- 학교급 맞춤형 안전 관리
  - 유치원
    - 실내 생활공간(화장실, 급식실, 교실 등) 안전 점검 강화
    - 동적 활동(놀이, 체육 등) 시간에 교사 매치 확대
    - 미끄럼 방지, 모서리 보호, 온도 및 열 관리 철저
  - 초중고
    - 체육 활동 전 안전교육 및 보호장비 착용 의무화
    - 과학실 및 실험실 안전장치 점검
    - 운동장 및 체육관 시설물 정기 점검 및 응급 처치 체계 강화
   
- 시간대 기반 안전 정책
  - 유치원: 다양한 시간대에 사고가 발생 > 전일 상시 안전관리 체계 필요
  - 초중고: 특정 시간대에 사고 집중 > 행사 전, 후 장전 점검 및 지도 강화
 
- 사고 형태별 대응
  - 유치원: 생활 안전에 중점
  - 초중고: 충돌 및 추락 예빵을 위한 안전 규칙 강화, 보호장비 착용 의무화

## 📌 정리 및 배운점

- **보상 데이터의 활용이 아쉬움**
  - 보상 데이터에 있는 급여 항목을 사용하였다면 더욱 좋은 분석이 되었을 것 같음.
  - 정보 중에서도 중요한 정보를 하나 버리고 시작하는 분석이라 많이 아쉬움이 남는다.
 
- **유치원과 초중고간의 비율 차이에 대한 조치를 취하지 않은 것**
  - 유치원생과 초중고생간의 비율 차이가 많이 나 이들의 차이에 대한 조치(sampling 등)를 취하지 않은 것이 아쉽다.
  - 모델의 성능 자체고 AUC 0.90이상 되지 않고(절대적 지표가 아니지만) 이에 따라 과적합이 생겨 일반화에 문제가 있을 수 있다.

 
- **배운점**
  - **Shapvalue dependence plot 실무 적용**
    - 실제로 shap value의 dependence plot을 적용해봄으로써 변수들 간의 관계를 시각적으로 확인하는 경험이 되었음
    - 추가로 해석 방법과 전략을 알 수 있게 됨.
   
  - **검증 설계와 데이터 누수 방지의 필요성**
    - 동일 학교, 학급 동일 시점의 표본이 학습 검증에 동시에 들어가면 과대 평가될 수 있음을 확인
    - 다음 과제에서는 GroupKFold, 시간 기준 시계열 분할(Temporal CV) 그리고 PR-AUC 드 처럼 비용 민감도에 맞는 지표를 함께 사용해 현업 적합도를 높혀볼 계획
   
  - **해석 가능한 feautre 엔지니어링 효과**
    - 단순 category보다 파생 변수등을 통해 예측력과 설명력을 동시에 끌어올릴 수 있음을 확인
    - 다음에는 SHAP + PDP/ICE 등 전통적 XAI도 활용하여 측정 feature 변화가 위험도에 미치는 정량 효과를 정책 문장으로 바로 번역하는 흐름을 확인할 것
