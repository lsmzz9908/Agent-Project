# trading_bot_kiwoom

키움 Open API+ (영웅문4) 기반 국내주식 스윙 자동매매 프로젝트 스캐폴드입니다.

## 설치
1. Windows 10/11 + 영웅문4 설치/업데이트
2. OpenAPI+ 서비스 등록
3. Python 3.10+ (실거래는 Windows + PyQt5/QAx 필수)
4. 의존성 설치
```bash
pip install pyqt5 pywin32 pandas numpy pyyaml sqlalchemy pytest
```

## 실행
```bash
python -m src.main --config config/config.yml
python -m src.main --config config/config.yml --run_mode backtest
```

## 모드
- backtest: 샘플 일봉 기반 신호 검증
- paper: 전략 신호 + 가상 주문/DB 기록
- live: Kiwoom API 로그인 후 주문 루틴(환경 미충족 시 stub)

## Live 주의사항
- 반드시 소액으로 1주 이상 검증 후 확대
- 장 시간/동시호가/시간외 제한 검증
- 중복주문 방지(idempotency), 상태머신, chejan 이벤트 처리 로그를 매일 확인
- 거래가 없는 날도 heartbeat/no_trade_today 로그로 정상 동작 여부 확인
