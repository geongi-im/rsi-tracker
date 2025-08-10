# RSI Tracker

## 프로젝트 개요

RSI Tracker는 주식 시장의 RSI(Relative Strength Index) 지표를 자동으로 계산하고 모니터링하는 파이썬 애플리케이션입니다. 설정된 주식 심볼들의 RSI 값을 실시간으로 추적하여 과매수/과매도 상황을 감지하고, 텔레그램을 통해 알림을 전송합니다.

또한 VIX(변동성 지수)와 CNN의 Fear & Greed Index(FGI)를 함께 표시하여 시장 심리를 종합적으로 파악할 수 있도록 메시지에 포함합니다. 전송 메시지 제목은 "미국 시장 현황 분석"이며, 섹션 순서는 RSI → VIX → F&G 입니다.

## 주요 기능

- 📊 **RSI 계산**: 표준 Wilder's Smoothing Method를 사용한 RSI 계산
- 📈 **다중 심볼 지원**: SPY, QQQ, DIA 등 여러 주식 심볼 동시 모니터링
- 🚨 **알림 시스템**: 과매수(70 이상)/과매도(30 이하) 상황 텔레그램 알림
- 🔧 **환경 설정**: .env 파일을 통한 유연한 설정 관리
- 📝 **로깅**: 상세한 로그 기록을 통한 실행 상황 추적
- 🧪 **테스트 모드**: 시스템 테스트용 별도 실행 모드
- 🌪 **VIX 변동성 지표**: `^VIX` 종가 수집 및 구간 기반 상태 분류
- 🧭 **Fear & Greed Index**: CNN FGI 수치 수집 및 상태 분류

## 시스템 요구사항

### 파이썬 버전
- **Python 3.10 이상** (필수)
  - ta 라이브러리 사용을 위해 Python 3.10 버전이 필요합니다
  - numpy, pandas 등의 최신 라이브러리와의 호환성을 위해 권장됩니다

### 의존성 패키지
```
yfinance>=0.2.18     # 주식 데이터 수집
pandas>=2.0.0        # 데이터 처리
numpy>=1.24.0        # 수치 계산
python-dotenv>=1.0.0 # 환경 변수 관리
requests>=2.31.0     # HTTP 요청
pymysql>=1.1.0       # MySQL 데이터베이스 연결
ta>=0.10.2           # 기술적 분석 지표 계산
fear-and-greed>=0.3.0 # CNN Fear & Greed Index 수집
```

## 설치 및 설정

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/rsi-tracker.git
cd rsi-tracker
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가합니다:

```env
# RSI 계산 설정
RSI_PERIOD=14
RSI_OVERSOLD_THRESHOLD=30
RSI_OVERBOUGHT_THRESHOLD=70

# 텔레그램 설정
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_CHAT_TEST_ID=your_test_chat_id_here
```

### 4. 텔레그램 봇 설정
1. [@BotFather](https://t.me/botfather)에게 메시지를 보내 새 봇을 생성
2. 생성된 봇 토큰을 `.env` 파일에 추가
3. 봇과 채팅을 시작하고 채팅 ID를 확인하여 `.env` 파일에 추가

## 사용법

### 일반 실행
```bash
python main.py
```

### 테스트 모드 실행
```bash
python main.py --test
```

## 프로젝트 구조

```
rsi-tracker/
├── main.py                 # 메인 실행 파일
├── rsi_calculator.py       # RSI 계산 로직
├── vix_analysis.py         # VIX 수집/분류 로직
├── fear_greed_fetch.py     # CNN FGI 수집/분류 로직
├── requirements.txt        # 의존성 패키지 목록
├── README.md              # 프로젝트 문서
├── .env                   # 환경 변수 (생성 필요)
├── logs/                  # 로그 파일 저장 디렉토리
└── utils/                 # 유틸리티 모듈
    ├── api_util.py        # API 호출 유틸리티
    ├── db_manager.py      # 데이터베이스 관리
    ├── logger_util.py     # 로깅 유틸리티
    └── telegram_util.py   # 텔레그램 메시지 전송
```

## 메시지 구성

- 제목: "📊 미국 시장 현황 분석"
- 섹션 순서: RSI → VIX → Fear & Greed Index
  - RSI: 각 지수의 RSI 값, 현재가, 상태(과매도/정상/과매수)
  - VIX: VIX 종가와 상태(매우 안정/안정/경계/불안/위기)
  - Fear & Greed: 지수 값과 상태(극단적 공포/공포/중립/탐욕/극단적 탐욕)

## 주요 클래스 및 메서드

### RSICalculator
- `calculate_rsi()`: 표준 Wilder's Smoothing Method로 RSI 계산
- `calculate_rsi_ta()`: ta 라이브러리를 사용한 RSI 계산
- `get_stock_data()`: Yahoo Finance에서 주식 데이터 수집
- `get_rsi_for_symbol()`: 특정 심볼의 RSI 계산
- `get_rsi_for_symbols()`: 여러 심볼의 RSI 일괄 계산

### TelegramUtil
- `send_message()`: 일반 메시지 전송
- `send_test_message()`: 테스트 채팅방으로 메시지 전송
- `send_photo()`: 이미지 전송
- `send_multiple_photo()`: 여러 이미지 동시 전송

### ApiUtil
- `create_post()`: API를 통한 게시글 생성

## 모니터링 대상 심볼

기본적으로 다음 ETF들을 모니터링합니다:
- **SPY**: S&P 500 ETF
- **QQQ**: NASDAQ-100 ETF
- **DIA**: Dow Jones Industrial Average ETF

심볼은 `main.py`의 `symbols` 리스트를 수정하여 변경할 수 있습니다.

## 지표 기준

- VIX 상태 분류
  - 0 ~ 15: 매우 안정
  - 15 ~ 20: 안정
  - 20 ~ 30: 경계
  - 30 ~ 40: 불안
  - 40 이상: 위기

- Fear & Greed Index 상태 분류 (0~100)
  - 0 ~ 24: 극단적 공포 (Extreme Fear)
  - 25 ~ 44: 공포 (Fear)
  - 45 ~ 55: 중립 (Neutral)
  - 56 ~ 75: 탐욕 (Greed)
  - 76 ~ 100: 극단적 탐욕 (Extreme Greed)

## 알림 조건

- **과매도 알림**: RSI ≤ 30 (기본값)
- **과매수 알림**: RSI ≥ 70 (기본값)
- **정상 상황**: 일일 현황 보고

알림 임계값은 `.env` 파일에서 `RSI_OVERSOLD_THRESHOLD`와 `RSI_OVERBOUGHT_THRESHOLD`로 조정할 수 있습니다. 현재 알림 트리거는 RSI 기준에 한해 동작하며, VIX/FGI는 현황 제공 용도로 메시지에 포함됩니다.

## 로그 관리

- 로그 파일은 `logs/` 디렉토리에 저장됩니다
- 실행 상황, 오류, RSI 계산 결과 등이 기록됩니다
- 로그 레벨은 `utils/logger_util.py`에서 설정할 수 있습니다

## 자동화 설정

시스템에서 자동으로 실행하려면 cron(Linux/Mac) 또는 Task Scheduler(Windows)를 사용하여 스케줄링할 수 있습니다.

예시 cron 설정 (매일 오후 4시 실행):
```bash
0 16 * * * cd /path/to/rsi-tracker && python main.py
```

## 문제 해결

### 주요 에러 및 해결 방법

1. **Python 버전 호환성 문제**
   ```
   ModuleNotFoundError: No module named 'ta'
   ```
   - Python 3.10 이상 버전 사용 확인
   - `pip install ta>=0.10.2` 재실행

2. **텔레그램 전송 실패**
   - 봇 토큰과 채팅 ID 확인
   - 봇이 채팅방에 추가되어 있는지 확인

3. **주식 데이터 수집 실패**
   - 인터넷 연결 상태 확인
   - 심볼명이 올바른지 확인
