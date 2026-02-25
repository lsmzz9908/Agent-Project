from src.levels.engine import LevelEngine

def test_level_engine_runs():
    s=[1,2,3,2,1,2,3,2,1]
    levels=LevelEngine().build(s)
    assert isinstance(levels, list)
