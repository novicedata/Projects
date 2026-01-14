# [상품 개발/Modeling] LIFECOMPASS: 나만의 자산 나침반

최종 결과 : 진행중

- [`Presentation`](https://github.com/novicedata/Projects/blob/main/Hanwha_Future_Talent/LIFECOMPASS_ppt.pdf)
- [`Youtube`](youtube.com/watch?si=8pM3zLkZ-vtK6JnH&v=yAAWqY_RaX8&feature=youtu.be)
- [`Quick Start`](https://github.com/novicedata/Projects/blob/main/Hanwha_Future_Talent/quick_start/quick_start.ipynb)
- Architecture
<p align = 'center'>
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/33c0ac04-3abc-4049-84f8-cbbb167ec8d8" /> </p>

## 목차

#### 1️⃣ 개요
#### 2️⃣ 데이터
#### 3️⃣ 전처리
#### 4️⃣ 국면 분류
#### 5️⃣ Policy 매핑
#### 6️⃣ 포트폴리오 제시(with XAI, LLM)
#### 📌 결과 및 결론
#### 📌 정리 및 배운점

---
<br>

### 1️⃣ 개요

- **기간 및 인원**: 2025.12.01-2026.01.09 / 3인
- **문제 정의**:
  - **필요성**:
    - 최근 금융 시장은 예측이 아니라 전환이 문제(금리 급변, 환율 등락, 정책/발언에 따른 순간적 국면 변화)
    - 기존 로보어드바이저의 문제는 과거 데이터 기반, 자산 배분의 이유 설명X, 손실 구간에서 고객 이탈 + 민원 + 규제의 리스크
    - 설명 불가능성은 사용자에게 불안을 야기하고 높은 만족도를 이끌지 못함
  - **연구 목적**:
    - 이미 많은 로보어드바이저가 예측성은 어느정도 지니고 있음. 우리는 판단자가 아닌 가설+근거+시나리오 기반 보조 역할을 하는 로보더으바이저를 제공하자함
    - 현재 설명가능한 국면 기반 AI에 대한 표준이 없음
    - 실제로 CFA Institue와 Bank of England를 포함한 글로벌 금융 기관들은 공통적으로 AI의 예측 성능이 아무리 높더라도 그 판단 과정을 설명할 수 없다면 규제와 신뢰의 장벽을 넘기 어렵다고 지적.
    <br>

- **제안 서비스**
  - **LIFECOMPASS**: 투자자의 이해와 신뢰를 함께 높일 수 있는 설명 가능한 금융 AI 서비스
    - **설명가능 AI**: XAI와 LMM을 활용하여 설명가능한 금융 AI 서비스를 구현
    - **UI/UX를 통한 이해**: 맑음/흐림/폭풍 등 날씨를 기준으로 나누어 주식 투자 시장의 상황을 한눈에 파악
    - **폭넓은 이용자층**: 주식 초보자부터 전문 투자자까지 수용하는 서비스 제안

- **주요 역할**:
  - 데이터 수집 및 전처리
  - 개인화 맞춤 모델 생성
  - XAI + LLM 적용 파이프라인 생성
  - 데이터 베이스 관리(SQL)
<br>

## 2️⃣ 데이터

- **데이터**
  - [Stooq](https://stooq.com/) 기반 금융 데이터
  - 2005년 ~ 2026년 금융 데이터
    - 현금, 금, 해외주식, 국내주식, 장기채 데이터
    - 각 일별 시작가, 마감가, 최고가, 최저가 value

<img width="557" height="395" alt="image" src="https://github.com/user-attachments/assets/893dc863-2263-497c-8b95-b14db8d81090" />

<br>

## 3️⃣ 전처리

- **요약**
  - 국면 분류, 포트폴리오 최적화, XAI의 공통 input data로 일별 데이터를 원 단위 feature 데이터로 전처리
  - mvp용 월말 기준 가격(1개월, 3개월, 12개월), 최근 3개월 변동성, 최근 6/12개월 최대 낙폭 데이터
 
- **데이터 월별 화**
  - 각 자산 데이터를 월별로 기준가, 변동성, 최대낙폭 정리
 
<img width="705" height="396" alt="image" src="https://github.com/user-attachments/assets/a64323b8-5fb8-42b6-a92a-b661f5558968" />


## 4️⃣ 국면 분류

- **규칙 기반 분류**
  - 국면 분류 모형을 따로 제작하여 클러스터링(데이터 기반) 방법을 사용할 수 있음.
  - 여기선 mvp용으로 시연 목적이 짙어 규칙 기반 시행
  - **국면 분류 목표**
    - : 월 1회 리밸런싱에 맞게 너무 빠르게 요동치지 않으면서도, 시장 변화(위험/추세)를 반영할 것
    - : LLM이 사용자에게 왜 이 포트폴리오인지 말해주기 위해 설명이 1문장으로 가능할 것.

  - 추세와 위험 두 축을 잡아 2 x 2 = 4가 나오도록
<p align = 'center'>
 <img width="403" height="350" alt="image" src="https://github.com/user-attachments/assets/ec99f95a-9151-45d8-af5d-86653706ecf1" /> </p>

## 5️⃣ Policy 매핑 모형 생성

- **국면과 사용자 성향에 따라 접근하는 Policy를 다르게**
- 각 Policy에 따른 ML/DL 모형이 사용가능하지만, 시연 목적으로 최대 3개의 서로 다른 모형을 설계하여 사용

<br>

- **CAR_RP**(CAP + Risk Parity): 변동성을 기반으로 배분하되, 주식 합 상한/하한 제약을 걸음
- **PRED_MVO**(예측 기반 Mean - Varianve): 다음달 기대 수익을 ML로 예측, 예측값과 공분산으로 MVO 최적화
- **MDD_GUARD**(자본보존/낙폭방어): 낙폭 스트레스가 큰 국면에서 현금/채권/금 중심으로 방어

<p align = 'center'>
<img width="580" height="203" alt="image" src="https://github.com/user-attachments/assets/b99f963c-b2de-41b4-9b70-56504ad40b7d" /> </p>
<br>

## 6️⃣ 포트폴리오 제시(with XAI, LLM)

- 위 3가지 모형을 적합, 설계한 후
- 국면과 개인 투자 성향 조합별로 서로 다른 모형에 input
- output으로 포트폴리오를 반환함.
<p align = 'center'>
<img width="174" height="179" alt="image" src="https://github.com/user-attachments/assets/e84328f8-ef6e-4eec-a794-1f88d922069a" /> </p>

- **Kernel SHAP** 사용
  - 현재는 mvp 시연 목적으로 세가지 policy 중 한개만 ML을 사용하여 SHAP의 커널형 모형인 Kernel SHAP 사용
  - 포트폴리오를 y로 두고 나머지 월별 자산 정보 데이터를 X로 활용하여 XAI를 적용
<p aling = 'center'>
<img width="378" height="122" alt="image" src="https://github.com/user-attachments/assets/2d25e75e-9919-4c6c-9d12-2e8040c9d174" /> </p>

- **LLM** 적용
  - SHAP에서 얻은 결과와 국면, 사용자 성향 및 월별 자산 데이터를 활용하여 LLM 적용
  - Geminai 2.5 flash를 api로 끌고와 프롬프트 튜닝을 통해 사용자 친화적 언어로 포트폴리오 구성 이유를 설명해줌
 
<p align='center'>
<img width="786" height="789" alt="image" src="https://github.com/user-attachments/assets/c9798a56-c8c5-48f4-97d9-bac257904b0d" /> </p>


## 📌 결과 및 결론

- mvp 시연 결과 목표로 했던 국면 + 사용자 성향에 따른 맞춤형 포트폴리오 제시
- 그리고 XAI with LLM을 통한 사용자 친화적 설명 구현에 성공
- 단, 높은 예측력과 대리 모형이 아닌 제대로된 SHAP를 사용하기 위해선 모든 Policy에 ML/DL을 활용할 필요가 있음
- **UI/UX**
<img width="200" height="500" alt="image" src="https://github.com/user-attachments/assets/736148e9-08b4-42f3-809e-34c1b3740b93" />
<img width="200" height="500" alt="image" src="https://github.com/user-attachments/assets/5590f162-0037-40ca-b916-14af8ce0ab9c" />
<img width="200" height="500" alt="image" src="https://github.com/user-attachments/assets/6adf9161-96f6-4a1b-acdd-5ac2bbdfa77b" />
<img width="200" height="500" alt="image" src="https://github.com/user-attachments/assets/8b34c3b2-e14a-40fd-83ab-185bacb80dd3" />


## 📌 정리 및 배운점

- **SQL 활용 중요성**
  - 데이터 수집 및 전처리와 결과 모두 SQL 데이터 베이스를 활용하여 정리하였음
  - 해당 과정이 데이터를 효율적으로 관리할 수 있고 notebook이 아닌 py 모형 시행과정에서 더더욱 중요함을 확인
 
- **Pipeline 구축**
  - mvp 시연을 위한 init, kernel, library 관계를 알게 되었고 이를 활용할 수 있게 됨
  - input에 따른 목표 output 도출을 위한 파이프 라인 설계 능력 향상
 
- **금융계 복잡성**
  - 금융권의 데이터를 어떻게 다루어야 하고, 어떤 모형들이 있으며
  - 각 모형의 장단점을 학습할 수 있게 되었음
