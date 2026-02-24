from __future__ import annotations
import argparse
from pathlib import Path
from .common.logger import setup_logger
from .kiwoom.kiwoom_api import KiwoomAPI
from .kiwoom.broker_kiwoom import KiwoomBroker
from .storage.repo import Repository
from .execution.idempotency import IdempotencyService
from .execution.order_manager import OrderManager
from .strategy.combo_sr_rsi_swing import ComboSRSRsiSwing
from .data.marketdata import MarketDataService
from .backtest.engine import BacktestEngine
from .universe.hybrid import HybridUniverse


def _load_config(path):
    try:
        import yaml
        return yaml.safe_load(open(path, encoding='utf-8'))
    except Exception:
        text=Path(path).read_text(encoding='utf-8')
        run_mode='paper'
        if 'run_mode: "backtest"' in text: run_mode='backtest'
        if 'run_mode: "live"' in text: run_mode='live'
        return {
            'app': {'run_mode': run_mode, 'market_mode': 'KR'},
            'logging': {'level':'INFO','log_path':'logs/bot.jsonl','heartbeat_log':True},
            'storage': {'db_path':'data/trading.db'},
            'universe': {'whitelist_symbols':['005930','000660']},
            'idempotency': {'key_template':'{date}:{symbol}:{side}:{signal_hash}'},
        }

def run(config_path, run_mode_override=None, market_mode_override=None):
    cfg=_load_config(config_path)
    if run_mode_override: cfg['app']['run_mode']=run_mode_override
    if market_mode_override: cfg['app']['market_mode']=market_mode_override
    logger=setup_logger(cfg['logging']['level'], cfg['logging']['log_path'])
    repo=Repository(cfg['storage']['db_path'])
    symbols=HybridUniverse(cfg['universe']['whitelist_symbols']).get_symbols()
    strategy=ComboSRSRsiSwing(); mds=MarketDataService()

    run_mode=cfg['app']['run_mode']
    logger.info('heartbeat', extra={'extra':{'universe_count':len(symbols), 'run_mode':run_mode}})

    if run_mode=='backtest':
        sigs=BacktestEngine().run(symbols,strategy,mds)
        logger.info('backtest_done', extra={'extra':{'signals_found':len(sigs)}})
        return

    api=KiwoomAPI(logger); broker=KiwoomBroker(api,logger); broker.login()
    idem=IdempotencyService(cfg['idempotency']['key_template'])
    om=OrderManager(repo, broker, idem, logger)
    trades=0
    for s in symbols:
        sig=strategy.evaluate(s, mds.get_daily(s))
        if sig:
            repo.insert_signal(sig)
            om.place_entry(sig, qty=1)
            trades += 1
    if trades==0 and cfg['logging'].get('heartbeat_log',True):
        logger.info('no_trade_today', extra={'extra':{'evaluated_symbols':len(symbols), 'signals_found':0}})


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--run_mode')
    p.add_argument('--market_mode')
    args=p.parse_args()
    run(args.config, args.run_mode, args.market_mode)

if __name__=='__main__':
    main()
