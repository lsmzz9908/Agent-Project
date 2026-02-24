# Shinhan Swing Trading Bot

Python 기반 스윙 자동매매 프로그램 골격입니다.

## 실행
```bash
cd trading_bot
python -m src.main --config config/config.yml
```

## 모드
- `run_mode`: backtest | paper | live
- `market_mode`: KR | OVERSEAS(US) | BOTH
- BOTH 모드는 KR/US 시장 루프를 분리 운영합니다.

## 설정
- 전략/리스크/유니버스/백테스트 파라미터는 `config/config.yml`에서 조정
- 민감정보는 `config/secrets.env.example`를 복사한 `.env`에 입력

## Live 주의사항
- 신한 API 인증토큰 자동 갱신 구현
- 주문 실패 시 백오프 재시도 구현
- 실거래 전 **소액 테스트**를 권장
