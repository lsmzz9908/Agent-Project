# trading_bot_kiwoom

키움 Open API+ (영웅문4) 기반 국내주식 스윙 자동매매 프로젝트입니다.

## 중요
- **live 모드는 Windows 전용**입니다. (영웅문4 + OpenAPI+ + PyQt5/QAxWidget 필요)
- Linux/macOS에서는 `backtest/paper` 확인만 권장하며, 실연동 로그인/주문은 동작하지 않습니다.

## 설치
1. Windows 10/11 + 영웅문4 설치/업데이트
2. 키움 OpenAPI+ 서비스 등록
3. Python 3.10+
4. 의존성 설치
```bash
pip install -r requirements.txt
```

## 실행
```bash
python -m src.main --config config/config.yml
python -m src.main --config config/config.yml --run_mode backtest
python -m src.main --config config/config.yml --run_mode live
```

## Live 로그인/계좌 검증 동작
- `KiwoomAPI.connect_and_login()` 호출 시 `CommConnect()`로 로그인 창이 표시됩니다.
- 로그인 성공 시 `kiwoom_login_success` 로그 출력
- 이어서 `GetLoginInfo("ACCNO")` 호출, 성공 시 `account_list_loaded` 로그 출력
- 계좌번호가 비어 있으면 즉시 예외로 중단합니다.

## Live 주의사항
- 반드시 소액으로 1주 이상 검증 후 확대
- 장 시간/동시호가/시간외 제한 검증
- 중복주문 방지(idempotency), 상태머신, chejan 이벤트 처리 로그를 매일 확인
- 거래가 없는 날도 heartbeat/no_trade_today 로그로 정상 동작 여부 확인

## 텔레그램 알림
보안을 위해 토큰/챗ID는 **환경변수로만** 읽습니다.

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
```

`config/config.yml`
```yaml
telegram:
  enabled: true
  daily_summary_time: "15:50"
  throttle_seconds: 2
```

스모크 테스트:
```bash
python -m src.main --config config/config.yml --smoke_notify
```
- 환경변수가 없으면 경고 로그만 남기고 프로그램은 중단되지 않습니다.
