# axis_and_allies
predict and evaluate events in the board game Axis and Allies

Command line tool to evaluate probability of winning a battle, or quantify amount of damage an army will inflict.
  Assumes units with lowest hit probability are removed first.
  
Input # of units and dice roll they "hit" on. AKA, it is general enough to handle different versions of the game.

Finer points like opening fire, the inability of planes to take new territory, etc have not been implemented.
Update Dec 2021: opening fire has mostly been implemented 
    (there is still some inaccuracy when planes are in the opposing fleet to a submarine sneak attack)
