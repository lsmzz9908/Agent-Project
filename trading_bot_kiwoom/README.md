# trading_bot_kiwoom

키움 Open API+ (영웅문4) 기반 국내주식 자동매매 프로젝트입니다.

## 중요
- **live/UI 모드는 Windows 전용**입니다. (영웅문4 + OpenAPI+ + PyQt5/QAxWidget 필요)
- Linux/macOS에서는 `backtest/paper` 확인만 권장합니다.

## 설치
1. Windows 10/11 + 영웅문4 설치/업데이트
2. 키움 OpenAPI+ 서비스 등록
3. Python 3.10+
4. 의존성 설치
```bash
pip install -r requirements.txt
```

## CLI 실행
```bash
python -m src.main --config config/config.yml
python -m src.main --config config/config.yml --run_mode backtest
python -m src.main --config config/config.yml --run_mode live
python -m src.main --config config/config.yml --smoke_notify
```

## UI 실행 (버튼형)
```bash
python -m src.ui.app
```
또는 Windows에서 `run_ui.bat` 더블클릭.

### UI 기능
- `[로그인]`: 키움 로그인 선행
- 모드 선택 라디오: `스윙 배치형` / `상시 실행형`
- `[선택 모드 시작]`: 선택 모드 실행
- `[종료]`: 루프 종료 + API close
- `[알림 테스트]`: 텔레그램 smoke 알림(telegram.enabled와 무관하게 테스트 전송 시도)
- 유니버스 관리:
  - KOSPI200 로드
  - 커스텀 txt/csv 로드
  - 종목 추가/삭제
  - 커스텀 저장(`data/universe/custom.txt`)

### UI 상태 표시
- 로그인 상태(시작/성공/실패)
- 선택 계좌(마스킹)
- 현재 모드
- 유니버스 종목 수
- 최근 평가/주문/체결 시각
- 금일 신호/주문/체결 수

## 유니버스
- 기본 파일: `data/universe/kospi200.csv` (또는 `data/universe_kospi200.csv`)
- UI에서 선택한 유니버스가 실행 시 우선 적용됩니다.

## 텔레그램 설정
민감정보는 코드/깃에 넣지 말고 `telegram.env.txt`로 관리하세요.

`telegram.env.txt` (프로젝트 루트):
```txt
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

`config/config.yml`:
```yaml
telegram:
  enabled: false
  daily_summary_time: "15:50"
  throttle_seconds: 2
```

- notifier는 전송 성공/실패를 로그(`telegram_send`)로 남깁니다.
- 알림 실패는 경고만 남기고 프로그램은 계속 실행합니다.

## Live 주의사항
- 반드시 소액으로 1주 이상 검증 후 확대
- 장 시간/동시호가/시간외 제한 검증
- 중복주문 방지(idempotency), 상태머신, chejan 이벤트 처리 로그를 매일 확인
