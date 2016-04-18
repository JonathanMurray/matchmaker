# Matchmaker
###### "An MMR- and matchmaking Python framework for team-based multiplayer games."

---

This project lets you try out different algorithms for matchmaking
 (constructing fair games) and MMR-scoring (adjusting players' ratings
 based on their wins/losses). Environmental settings, such as skill distribution
 in the player population, and players' gaming-duration habits, are also configurable.
 Using pygame, the performance of a matchmaker can also be shown in real-time.

---

##### Project structure:
 * "Engine" (the main class) delegates work to other more specialised classes
 * "Environment" controls the players' behaviour outside of games, and determines game outcomes.
 * "Matchmaker" is responsible for matching players from the queue into new games, prioritizing short wait times and fair games.
 * "MmrEngine" is responsible for adjusting the MMR-ratings of individual players from the winning/losing team after a game has finished.

 MatchMaker and MmrEngine are meant to be supplied by the user (although there are available default versions)

 ### Getting started / things to do:
* Run the code in main.py, try out different available matchmakers
* Start a graphic demo of a matchmaker using the Demo-class
* Write your own matchmaker (extending the class MatchMaker)
* Write your own MMR-engine (extending the class MmrEngine)
* Write a more advanced/realistic environment than the default one
