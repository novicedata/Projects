
<details>
 <summary> preprocess.py </summary>

- input: 크롤링한 전체 리뷰 데이터
- output: 퍼스트 디센던트, 워프레임 각각 2(kor, eng) x 2(negatove, positive) 정제 텍스트 데이터

- 영어/한국어 리뷰만 추출
- 너무 짧은 리뷰 제거(5 letters)
- 감정 없는 데이터 제거
</details>

<details>
 <summary> sampling.py </summary>

- input: 전처리한 리뷰 데이터
- output: 6개 그룹별 균형 맞춘 랜덤 데이터 세트
  - low_churned, low_active
  - mid_churned, mid_active
  - high_churned, high_active

- 그룹: 3(리뷰 시점 플레이 시간 [10h / 10~50h / 50h+]) x 2(이탈 여부) 
</details>

<details>
 <summary> distill.py </summary>

- input: sampling 후의 리뷰 데이터
- output: 2-4 bullet points, 5-8 word phrase, evaluative adjective 포함, JSON 형식 데이터

- Ollama 호출
- 결과 파싱
- 로직: 체크포인트 로딩 -> 리뷰 하나씩 처리 -> llm 호출(사전 프롬프팅) -> 결과 저
</details>

<details>
 <summary> embedding.py </summary>

- input: sampling 후의 리뷰 데이터
- output: 2-4 bullet points, 5-8 word phrase, evaluative adjective 포함, JSON 형식 데이터

- Ollama 호출
- 결과 파싱
- 로직: 체크포인트 로딩 -> 리뷰 하나씩 처리 -> llm 호출(사전 프롬프팅) -> 결과 저
</details>
