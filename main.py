from core.demo import Demo
from core.matchmakers import fair_matchmaker, advanced_matchmaker2
from core.environments import BaseEnvironment
from core.runner import Runner
from myMatchMaker import MyMatchMaker


def get_statistics():
    runner = Runner()
    run2 = ("Fair", fair_matchmaker, BaseEnvironment())
    run3 = ("Test-matchmaker", MyMatchMaker(), BaseEnvironment())
    runner.run_and_plot([run2, run3])


def run_demo():
    demo = Demo()
    mm = advanced_matchmaker2
    env = BaseEnvironment()
    demo.run(mm, env)

run_demo()
