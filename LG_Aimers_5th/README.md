# LG_Aimers_5th
## 제품 이상 여부 판별 과제

![image](https://github.com/user-attachments/assets/47878eb6-db5b-40dc-8682-6d6223f92473)

예선 결과 : 56 / 740

## 팀원

김창우, 박인애, 신진영, 이승우, 이현주

## 문제 정의

제품 이상 판별 프로젝트로 공정별 데이터 세트(총 4단계로 Dam, AutoClave, Fill1, Fill2)가 주어진다.

일부 공정 데이터만 주어지며 가능한 불량 유형이 한정된다. 불량이 어떤 유형의 불량인지는 알 수 없으며 크게 정상/불량의 이진 분류가 목적이다.

성능지표는 AUC-ROC

## 접근 방법

### 데이터 확인 및 전처리

- Trian data : 40,506 rows
- Test data : 17,361 rows
- Features : 464 columns

- Imbalanced : 38,156(Normal), 2,350(AbNormal)

- 대부분이 범주형 데이터고, 같은 비율을 가진 범주형 데이터가 다수 존재 -> 전처리
- 결측값이 다수 존재 -> **데이터 수기 확인 결과 변수 열이 밀린 것을 확인 후 정제**
- 이상치 처리, 다중공선성 확인, 공정별 중복되는 범주형 데이터 처리
- 불균형 데이터 오버샘플링, 언더샘플링 시도
- 정규화, PCA 등 시도

### 도메인 지식

- 도메인 지식이 부족하기에, 도메인 지식을 서칭 -> 각 공정별 단계가 어떤 것이고 데이터 프레임의 변수들이 어떤걸 의미하는지 확인 (https://youtu.be/JOuV4HuKQds?si=-Emi4eiEegSqQvWI, https://youtu.be/feNewpVvC5M?si=6nKSvJ8f6jW_CXUd)
- 불량 판별에 유의미할 변수들을 확인

### 성능 향상 중요 포인트

- feature importance check
- correlation check
- making erived variable
- 범주형 변수이기 때문에 CATBoost의 적극 사용

### 모델링

- CV
- Ensemble(Soft voting, Hard voting, Boosting, Stacking)

## Presentation
[PPT](presentation/LGAimers5_presentation.pdf)
