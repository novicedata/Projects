# [매출데이터/클러스터링, 연관성 분석] 구매 데이터 활용. 매출 상승 전략 프로젝

## 목차

### 1️⃣ 개요
### 2️⃣ 데이터
### 3️⃣ 전처리 및 EDA
### 4️⃣ 클러스터링
### 5️⃣ 프로파일링
### 6️⃣ 분류 
### 7️⃣ 연관성 분석
### 8️⃣ 결과


### 📌 결론
### 📌 정리 및 배운점
<br>

## 1️⃣ 개요

- **배경**:
  - 오프라인 유통사에서 VVIP 고객 수가 지속적 증가
  - VVIP 전용 서비스(라운지, 전담 응대 등) 이용 고객 급증
    - 서비스 대기 불만 증가
    - CS 지속 발생
    - 서비스 관리 비용 증가
    - 1인당 서비스 인단가 하락

 - **문제 정의**
   - 현재 VVIP 등급 기준이 적절한가?
   - VVIP 고객은 실제로 구매 여력이 모두 소진된 상태인가?
   - 등급 달성 이후 구매가 정체되는 현상이 존재하는가?
  
- **최종 문제 정의와 해결 방안**
  - VVIP 등급 기준을 데이터 기반으로 재설계
  - 고객 이탈 최소화 + 업셀링 매출 극대화할 수 있는 최적 기준 도출
  - 해결 방안
    - 구매 여력 함수 적합 -> 클러스터링 -> RF 분류 -> 기준 상향 시뮬레이션 -> 업셀링 금액 추정
  
<br>

## 2️⃣ 데이터

- **데이터**
  - VVIP 롱폼 데이터: 고객 ID, Date, Sales (390,330 x 3)
    > <img width="265" height="205" alt="image" src="https://github.com/user-attachments/assets/8f47c556-4a95-4882-bf1a-4345f639cdef" />

  - VVIP 구매 데이터: 고객 ID, 제품 카테고리 별 매출, 매출 합계 (4,197 x 28)
    > <img width="848" height="145" alt="image" src="https://github.com/user-attachments/assets/4e9b20d2-b14b-4bf9-91a6-7b39c5dfb090" />

  - VVIP 인구통계학 데이터: 고객 ID, 거주지, 나이 (4,197 x 3)
    > <img width="240" height="144" alt="image" src="https://github.com/user-attachments/assets/87fca95a-6503-4817-9a8f-d5676021d4b9" />

  - VVIP 연도별 매출 집계 데이터: 고객 ID, 거주지, 나이, 19년 ~ 22년 연도별 매출 총액, 19년 ~ 22년 연도별 구매 건 (4,197 x 13)
    > <img width="846" height="175" alt="image" src="https://github.com/user-attachments/assets/a3413bfb-b65c-4e0a-947c-9547f522088b" />

  - VVIP 상품 단위 거래 데이터: 고객 ID, 날짜, 물품 카테고리, Sales, Count (43,736 x 5)
    > <img width="391" height="114" alt="image" src="https://github.com/user-attachments/assets/3e3cbbbf-0a8d-4ffa-bb2f-069f03fdaf49" />

<br>

## 3️⃣ 전처리 및 EDA

- **누적 방문 횟수 x 누적 매출 확인**
  - 각 고객 ID 별로 각 월 별 누적 방문 횟수와 누적 매출간의 관계를 시각화
    - 데이터를 목적에 맞게 변형후 산점도 및 로그 회귀선 확인
      > <img width="449" height="282" alt="image" src="https://github.com/user-attachments/assets/96e83d1f-0969-49ef-81bf-8a1ba65cdb0f" />
      > <img width="450" height="350" alt="image" src="https://github.com/user-attachments/assets/79cb47b0-f2a4-47d8-968e-583907d2cfeb" />

  - 현재 가정한 VVIP 누적 매출이 1.5억. 약 1.3억 근처부터 방문 횟수에 비해 누적 매출이 늘지 않는 형태를 보이고 있음.


<br> 

## 4️⃣ 클러스터링

- **VVIP 구매 이력 파악**
  - 이용 고객 패턴별 클러스터링을 통해 후에 할 연관성 분석과 연결하여 클러스터별 맞춤형 전략을 세우고자 함.
  - 총 26개의 카테고리를 대분류로 합쳐 총 12개의 카테고리로 범주화
  - 스케일링 전 박스 플롯
    > <img width="600" height="400" alt="image" src="https://github.com/user-attachments/assets/5d98cc20-0730-4248-a0b7-4cd3b0aef687" />

  - 패턴을 더 확실하게 보기 위해 이상치 제거, Min-Max 스케일링 후 박스 플롯 확인
    > <img width="600" height="400" alt="image" src="https://github.com/user-attachments/assets/2e57da5f-7f67-4a9e-9b49-a106ba4cf14a" />

  - 전체적으로 명품 소비보다는 장보기/식사 및 패션 의류 관련 매출이 응집되어 있음.
  - 리빙합의 경우 생활가전이기 때문에 매출 평균 자체가 높게 측정 된듯함
  - 나머지는 평탄한 분포
 
- **클러스터 개수 탐색 및 시행**
  - elbow method + 실루엣 확인
  - 실루엣 기준 클러스터 3으로 선
    > <img width="400" height="250" alt="image" src="https://github.com/user-attachments/assets/3613b21d-d734-4311-a7d6-eb1fe9b03331" />
    > <img width="400" height="250" alt="image" src="https://github.com/user-attachments/assets/ab02d100-f0a6-44f2-87f5-da87ea90dbbf" />

  - Kmeans 활용하고 PCA를 통해 2차원 시각화
    > <img width="500" height="350" alt="image" src="https://github.com/user-attachments/assets/39ce4677-dc26-49ea-9cd6-14049520f172" />


<br>


## 5️⃣ 프로파일링

- 클러스터별 카테고리 평균화한 후 시각화 하여 확인
  > <img width="835" height="406" alt="image" src="https://github.com/user-attachments/assets/a1d5856a-5ea7-45d5-82cc-41006a88f842" />

- 원 스케일로는 확인하기 어려워 Min-Max 스케일링 한 값으로 확인
  > <img width="833" height="405" alt="image" src="https://github.com/user-attachments/assets/dd7eb5ca-1902-445f-ab86-6201506f7347" />

- 인구통계학 정보 포함하여 클러스터별 프로파일링 정리
  > <img width="400" height="120" alt="image" src="https://github.com/user-attachments/assets/8c7141bb-f292-492b-92d8-5fe2d1280599" />
  > <img width="500" height="280" alt="image" src="https://github.com/user-attachments/assets/58e7ec3c-949f-4e7e-aa31-3587dd94374c" />
  > <img width="500" height="280" alt="image" src="https://github.com/user-attachments/assets/f118bce8-df0b-49fb-88b0-49f3298f760f" />
  > <img width="500" height="280" alt="image" src="https://github.com/user-attachments/assets/d13f38b5-421d-493d-89ba-8381e4b04470" />
  > <img width="500" height="280" alt="image" src="https://github.com/user-attachments/assets/5192fc69-b378-4e90-8a1c-9d72ccd085d9" />
  > <img width="500" height="280" alt="image" src="https://github.com/user-attachments/assets/974cb76d-a11c-4a65-afc3-ecc21509fc6f" />
  > <img width="500" height="280" alt="image" src="https://github.com/user-attachments/assets/67461389-77db-4e73-9c6c-859fb437bac0" />

- 목적형(클러스터 1): 매출의 약 14%. 대부분 뷰티 악세서리를 구매하며 40대가 대부분.
- 생활형(클러스터 2): 매출의 약 36%. 리빙과 패션 그리고 아동스포츠 등 생활에 필요한 용품 구매. 50대 이상이 과반수 포함
- 가정형(클러스터 3): 매출의 약 50%. 클러스터 2와 소비 패턴이 유사하지만 식품류까지 구매. 가정을 책임지는 40대 이상


<br>

## 6️⃣ 분류 

- 클러스터 별 목표 매출 달성자를 확인하고 맞춤 캠페인 타겟을 확인
- **해당 과정에서 FP로 인해 생기는 비용(손실)을 계산**
  - 이를 위해 goal을 바꿔가며 "손실 vs 타겟 규모" 트레이드 오프를 확인
    > <img width="444" height="261" alt="image" src="https://github.com/user-attachments/assets/dc72b3f7-6ce1-4830-9c80-6850a084e55f" />

- 1.5억 ~ 2억 사이 천만원 단위로 VVIP 선정 금액을 올려가며 확인.
  - 엑셀로 추출하여 결과 분석
    > <img width="1060" height="620" alt="image" src="https://github.com/user-attachments/assets/3c1eefaf-dc19-4ac9-b679-7b03dfa8b93b" />
    > <img width="869" height="381" alt="image" src="https://github.com/user-attachments/assets/75caeeb6-359a-45a5-b88c-a5dfb0b16a4b" />


- **결과적으로 1.8억 기준 관리 해야할 VVIP 고객수는 줄이면서도 기회 손실이 가장 높다.**

## 7️⃣ 연관성 분석

- 단순 상관을 넘어 구매 행동 패턴을 실제로 활용해보자.


|용어|뜻|의미|
|---|---|---|
|지지도|전체 거래 중 해당 항목이 함께 등장한 비율|전체 중 같이 산 비율|
|신뢰도|A를 샀을 때 B도 살 확률|A 산 사람 중 B산 사람은 얼마나?|
|향상도|A와 B가 독립적일때 보다 얼마나 더 많이 같이 등장하는지|우연 대비 몇 배 더 많이 샀는가?|


- 고객 id와 date를 묶어 당일 주문한 모든 카테고리를 items 칼럼으로 묶기
  > <img width="472" height="606" alt="image" src="https://github.com/user-attachments/assets/0fab3a2f-e3f7-4675-a4c3-4b1dd08540c0" />

- 원핫 인코딩 한후, Apriori를 통해 0.1% 이상 등장하는 조합만 후보로 등록
- 전체 규칙
  > <img width="414" height="300" alt="image" src="https://github.com/user-attachments/assets/430bf210-d3d6-49cd-8c28-14117142776b" />

- lift 1.0 이상인 리빙합/뷰티악세, 패션/아동스포츠가 뽑힘. 추천 후보.

- 클러스터 별로 보면
  > <img width="476" height="426" alt="image" src="https://github.com/user-attachments/assets/16496084-8f51-41ac-aebc-452c1fe1da39" />

- 각 클러스터 별로 lift 값의 차이는 있지만 조합자체는 유사하다.
  > 매출 업셀링을 위해 리빙 제품 구매시 뷰티 악세 쿠폰 지급하는 등 지출 유도가 가능할 듯.


## 8️⃣ 결과

- **매출 정체 구간 확인**
  - 1.3 ~ 1.5억 구간 이후 방문 대비 매출 증가율 둔화
 
- **VVIP는 3개 소비 유형으로 구분 가능**
  - 목적형/생활형/가정형으로 분리되어 소비 구조가 약간 상이함
 
- **클러스터별 매출 기여도 차이 존재**
  - 가정형이 전체 매출의 약 50%를 차지하는 핵심 집단

- **기준 상향 시 고객 수 감소 + 업셀링 유지**
  - 1.8억 기준 관리 인원은 줄고 기회손실(업셀 갭)은 최대
 
- **교차 구매 패턴 존재**
  - 리빙-뷰티, 패션-아동스포트 조합에서 lift > 1로 추천 가능성 확인
 
<br>

## 📌 결론

- **VVIP 기준 상향 조정 필요**
  - 1.8억으로 변경하는 것이 운영 효율과 매출 잠재의 균형점으로 보임.
 
- **FP 고객은 제거 대상이 아니라 업셀 타겟**
  - 기회손실은 실제 매출 전환 가능성이 높은 잠재수요임
 
- **클러스터 기반 차등 전략 필요**
  - 동일선상에 놓인 VVIP가 아니라 성향별 맞춤 캠페인이 효율 적일 것
  - 교차 구매 패턴에서 확인했듯, 리빙 제품 구매시 뷰티 제품 쿠폰 발행 등 소비 유도가 가능할 것.

- **등급 재설계는 비용 절감 + 매출 확대 전략**
  - 서비스 과밀 해소와 매출 증대 동시 달성 가능
 
- **교차 구매 패턴 존재**
  - 리빙-뷰티, 패션-아동스포트 조합에서 lift > 1로 추천 가능성 확인

    
## 📌 정리 및 배운점

- **카테고리화 중요성**
  - 목적에 맞게 카테고리 합치거나 세분화하는 과정이 분석 결과와 해석에 영향이 크다는 것을 확인
  - 같은 데이터라도 어떻게 분류하느냐가 인사이트 깊이와 해석 정확도를 크게 달리한다는 것을 깨달음
 
- **클러스터링, 프로파일링 실무적 고려**
  - 단순히 K-means 딱 코딩한다고 끝이 아니라, 어떤 변수 넣고 어떤 스케일링 적용하느냐가 해석력을 좌우
  - 실무에서 사용하려면 변수 선택, 이상치 처리, 군집 수 설정 등 설계 단계가 중요할 것 같음
 
- **목적 함수 기반 시뮬레이션의 가치**
  - 단순 분류 정확도를 보는게 아니라, 실제 KPI를 목표값으로 설정해 기준을 변화시키며 시뮬레이션 하는 방식이 실무에 더 적합할 수 있다는 점 배웠다.
 
- **연관성 분석을 통한 행동 패턴 이해**
  - 단순 상관을 넘어 실제 구매 조합을 기반으로 교차 판매 전략을 도출할 수 있다는 점에서 연관규칙 분석의 활용 가치 확인.

