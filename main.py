from core.demo import Demo
from core.engine import Engine
from core.matchmakers import fair_matchmaker, advanced_matchmaker2
from core.environments import AdvancedEnvironment, SimpleEnvironment
from core.mmr_engine import BaseMmrEngine
from core.runner import Runner
from myMatchMaker import MyMatchMaker


def get_statistics():
    runner = Runner()
    run2 = ("Fair", fair_matchmaker, AdvancedEnvironment())
    run3 = ("Test-matchmaker", MyMatchMaker(), AdvancedEnvironment())
    runner.run_and_plot([run2, run3])


def run_demo():
    demo = Demo(wait_ms=100, bar_height=10, bg_color=(30, 30, 80))
    mm = advanced_matchmaker2
    mmr_engine = BaseMmrEngine()
    env = SimpleEnvironment()
    demo.run(mm, mmr_engine, env, skip_rounds=60)


def test_mmr_engine():
    mm = advanced_matchmaker2
    mmr_engine = BaseMmrEngine()
    env = AdvancedEnvironment(100, 20)
    engine = Engine(mm, mmr_engine, env)
    for i in range(60*60*5):
        engine.one_round()
        if i % (60 * 10) == 0:
            print(int(i / (60*10)))
    for name in engine.players:
        p = engine.players[name]
        print(name + " - mmr (" + str(p.mmr) + "), skill (" + str(env.get_player_skill(name)) + ")")

run_demo()
