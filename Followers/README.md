# [SNS데이터/회귀] 인스타 계정 좋아요, 팔로우 분석

## 목차

### 1️⃣ 개요
### 2️⃣ 데이터
### 3️⃣ EDA
### 4️⃣ 회귀 모델링
### 5️⃣ 결과

### 📌 결론
### 📌 정리 및 배운점
<br>

## 1️⃣ 개요

- **문제 정의**:
    - 좋아요와 팔로워의 관계는?
      - 팔로워가 많으면 당연히 좋아요도 많은가?
    - 인플루언서 지표 자체는 무엇을 반영하고 팔로워가 많으면 무조건 높은건가? <br>
  
<br>

## 2️⃣ 데이터

- **데이터**
  - 인스타 계정 데이터 (200 rows x 10 columns)
  - 계정 info, 인플루언서 지수, 게시물 수, 팔로워 수, 평균 좋아요 수, Engagement rate, 새 게시물 평균 좋아요 수, 전체 좋아요, 국적
<br>

## 3️⃣ EDA

- **1. 결측치 처리 및 실수화**
  - 국적에 62개 NULL값 None으로 변경
  - m, k, b등 지수를 숫자로 변경
    > <img width="351" height="528" alt="image" src="https://github.com/user-attachments/assets/5c46f329-5bdc-4d20-aea6-b21aff7d7f15" />
    > <img width="647" height="580" alt="image" src="https://github.com/user-attachments/assets/3ec40054-9fd6-469a-a72c-eed40c1fa5e7" />

- **2. 팔로워 수에 비해 좋아요 수가 적은 계정 확인**
  > <img width="545" height="525" alt="image" src="https://github.com/user-attachments/assets/024d6d53-0cd9-46e9-85f1-f8396d76e6ca" />
  > <img width="944" height="425" alt="image" src="https://github.com/user-attachments/assets/1c51d25f-5a38-474b-9948-0e422940265d" />

  - 팔로워 수에 비해 반응이 적은 계정들이 존재한다.
    - 상위 10% 팔로워, 하위 10% 평균 좋아요 등 극단적인 값은 확인결과 존재하지는 않았다.
    - 4분위수 기준으로 존재하긴 하니 그럼 influence score를 확인해보면??
      - 과연 influence score 자체가 잘못된건가??
     
- **3. 팔로워 수가 많은 계정이 항상 높은 influence score를 가지는가 확인**
  > <img width="751" height="510" alt="image" src="https://github.com/user-attachments/assets/73679946-63d5-4701-87ef-b19b519134dd" />
  > <img width="453" height="79" alt="image" src="https://github.com/user-attachments/assets/d7c47b1d-7b59-4241-b595-927acb0a8f26" />

  - 상관은 0.368로 어느 정도 존재하긴 하다.
  - 다만, 그래프를 보면 알겠지만 팔로워가 적어도 높은 스코어를 가진 경우가 대부분이다.
  - 그럼 팔로워 대비 실제 반응이 높은 인플루언서는??

- **4. Engagement Rate(평균 좋아요/팔로워) 지표 만들어 확인**
  > <img width="552" height="692" alt="image" src="https://github.com/user-attachments/assets/3c67d4a1-062f-4c44-9b07-cde46ec2134e" />
  > <img width="865" height="521" alt="image" src="https://github.com/user-attachments/assets/8ec0a618-d586-4e5b-b086-c61abef7fa10" />

  - 상위 3명의 계정이 유독 높고 그 다음은 완만하게 내려가는 느낌
  
## 4️⃣ 예측 모델링

- **influence score를 target으로 회귀 후 영향요인 확인**
  > <img width="598" height="514" alt="image" src="https://github.com/user-attachments/assets/5cbbf59b-0e1f-4969-8ac9-740d3a2a92fd" />
  > <img width="1103" height="453" alt="image" src="https://github.com/user-attachments/assets/24bbbe68-4269-47bc-83fe-f2bf7b4eb042" />

  - 우선 R값 자체가 높지 않다. RMSE도 마찬가지로 그렇게 좋은 지표는 아닌 듯 하다.
  - 그래도 영향 요인을 RF에서 제공하는 Feature Importance로 간단하게 확인해보면
    > <img width="991" height="582" alt="image" src="https://github.com/user-attachments/assets/e9be3e7a-ce56-4df5-8434-09da448ccf05" />

  - 팔로워 수 자체가 압도적인 영향력을 보인다.
<br> 

## 5️⃣ 결과

- **팔로워가 많으면 좋아요도 많은가?**
  - 팔로워 수 대비 좋아요 반응이 낮은 계정이 분명 존재
  - 극단치와 같은 완전한 비정상 케이스는 아니지만 사분위수 기준 존재함

- **팔로워가 많으면 influence score가 높은가?**
  - 상관은 0.368로 중간 정도의 양의 관계는 존재함
  - 다만, 산점도 상 팔로워가 적어도 높은 influence score를 가진 계정이 다수 존재

- **Engagement rate로 본 진짜 반응 좋은 계정**
  - Eng rate기준 상위 3개 계정이 유독 튀는 형태임
  - 나머지는 완만하게 감소
  - 팔로워 규모와 별개로 팔로워 대비 반응이 좋은 소수 계정이 존재함을 확인
 
- **influence score 예측(회귀 결과)**
  - R, RMSE 성능 자체가 좋진않음
    - 현재 변수들만으로 정확히 설명하고 예측하긴 어려움
  - 그럼에도 Feature Importance 기준 팔로워 수가 압도적 1위
<br>

## 📌 결론

- **팔로워는 좋아요/영향력의 필요조건이라기 보단 부분 조건**
- **influence score는 팔로워 영향이 강하게 섞여있을 가능성이 큼**

- **다만 현재 데이터로는 일반화가 어려움**
  - 낮은 influence score 구간이 없어서 관계가 왜곡됏을 가능성이 충분히 존재 한다.

    
## 📌 정리 및 배운점

- **Tableau 계산된 필드 활용 능력**
  - 태블로에서 계산된 필드를 활용하여 str을 수치화하고 마크를 통해 시각화하는 능력 향상
 
- **데이터 수집의 중요성**
  - 목적에 맞는 데이터 수집하는 것이 중요하다.
  - influence score를 확인하고 싶었다면 낮은 score 값들도 수집했어야 한다.

