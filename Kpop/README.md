# [Youtube API 데이터/단순 비교 분석] BTS vs BLACKPINK youtube 조회수 분석
## 목차

### 1️⃣ 개요
### 2️⃣ 데이터
### 3️⃣ EDA
### 4️⃣ 결과

### 📌 결론
### 📌 정리 및 배운점
<br>

## 1️⃣ 개요

- **문제 정의**:
    - Kpop 선두주자인 BTS와 BLACKPINK 과연 youtube 기준 누가 더 글로벌 한가?
    - 단순한 흥미 + API 사용법 익히기 <br>
  
<br>

## 2️⃣ 데이터

- **데이터**
  - Google console, youtube 기반 각 그룹 플리 크롤링
  - 비디오 식별자, 제목, 업로드일, 총 조회수
    > <img width="1091" height="462" alt="image" src="https://github.com/user-attachments/assets/b4153221-d168-4c6e-bf76-c3a58c9ad8d3" />
    > <img width="1092" height="769" alt="image" src="https://github.com/user-attachments/assets/6f940c48-2bad-43d8-83a2-52cd89ae5d09" />

  - **BTS**: 2008년 6월부터 현재까지 총 3014개 영상(행)
  - **BLACKPINK**: 2016년 07월부터 현재까지 총 651개 영상(행)


<br>

## 3️⃣ EDA

- **1. 각 그룹 조회수 Top 10 확인**
  - 한글 글꼴 설정...
    > <img width="1013" height="833" alt="image" src="https://github.com/user-attachments/assets/29541522-bc74-4e0d-b634-123f0394af41" />

  - 각 순위별 비교해볼 때, 모든 영상에서 블랙핑크가 더 많은 것을 확인.

- **2. 전체 영상 조회수, 평균 조회수 확인**
  - 시각화 중 M, B 단위 사용
  > <img width="746" height="649" alt="image" src="https://github.com/user-attachments/assets/f757252e-9150-45d4-9b5a-3e8725e263aa" />
  > <img width="577" height="371" alt="image" src="https://github.com/user-attachments/assets/9b8a0b2b-53b9-454b-8c12-b6328c7eb7a9" />

  - 약 8년을 더 일찍 업로드했던 방탄이 전체 영상 조회수를 앞선다. 그 차이도 billion 기준이니 매우 크다.
  - 단, 영상별 평균 조회수는 블랙핑크가 앞선다. million 기준이라해도 그 차이가 상당함.
     
- **3. 시계열 차트로 업로드일 비교**
  > <img width="1095" height="752" alt="image" src="https://github.com/user-attachments/assets/2b6775b8-e084-4302-8dcf-fa1b6e60b226" />

  - 비교하기 힘드니 누적으로 한번 확인해보자
  - 아래 누적 조회수로 확인해보았을 때 방탄이 8년 일찍 했다고 하더라도 블랙핑크의 성장세가 매우 빠르다.
  - 심지어 2020년 - 2024년까지는 앞선 경우가 많다.
  - BTS가 군제대 후 때문인지 서서히 앞서는 중
    > <img width="1088" height="738" alt="image" src="https://github.com/user-attachments/assets/270435a2-6a9d-4f1c-9746-041ef099c165" />

  - 월 별로 평균 조회수 확인해보면.. 2025년 이후 잠깐 떠올랐던 블랭핑크 조회수가 눈에 띈다.
  - 확인 결과 오랜만에 단체 앨범인 'JUMP' 발매 시기였다.
    > <img width="1096" height="464" alt="image" src="https://github.com/user-attachments/assets/e00de89e-ab68-4855-906a-b3898c20392e" />
    > <img width="1141" height="448" alt="image" src="https://github.com/user-attachments/assets/e045ec32-948f-4855-8982-b867eb808670" />

  
## 4️⃣ 결과

- 방탄이 8년 더 빠르게 업로드를 시작했음에도 블랙핑크의 성장세가 매우 가파르다
<br>

## 📌 결론

- 전체 영상 조회수 자체는 BTS가 많으나, 평균 조회수는 BLACKPINK가 많다.
  - 이는 동일 영상수 기준이면 따라잡혔을 것.
 
- 하지만 제대한 방탄이 활동을 재개하면 따라잡기 힘들것 같다.

    
## 📌 정리 및 배운점

- **API, JSON 활용 능력**
  - API 키를 발급받고 적용하는데에는 다른 프로젝트도 몇번 해보니 익숙하다.
  - JSON 구조를 확인하고 이용하는 방법 능력이 향상.
 
- **matplotlib 시각화 능력**
  - seaborn 포함 python의 대표적 시각툴 활용 능력이 향상
  - 그래프 내부 지표 변경, 한글 글꼴 사용 등 활용

