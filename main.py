from core.matchmakers import fair_matchmaker
from core.environments import BaseEnvironment
from core.runner import Runner
from myMatchMaker import MyMatchMaker

runner = Runner()

run2 = ("Fair", fair_matchmaker, BaseEnvironment())
run3 = ("Test-matchmaker", MyMatchMaker(), BaseEnvironment())

runner.run_and_plot([run2, run3])
