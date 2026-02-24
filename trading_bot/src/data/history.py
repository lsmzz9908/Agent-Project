from __future__ import annotations
import pandas as pd

class HistoryLoader:
    def load_csv(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        df["ts"] = pd.to_datetime(df["ts"])
        return df.sort_values("ts").reset_index(drop=True)
