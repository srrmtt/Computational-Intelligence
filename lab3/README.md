# Lab 3 : Policy Serch
This code has been written by Serra Matteo s303513 and Magnaldi Matteo s296852 for the course of Computational Intelligence ay 2022-2023. The goal of this code is to play the nim game with an expert system or an evaluated rule strategy. To do that we wrote 3 methods:
- `expert_system` : this function use an informed system to make the next move, all the choices done in this function are made with the nim sum approach, if we specify a `k` as limit of elements to take this function will resolve the *subtractive game*. 
- the second approach use an evolutionary algorithm with tournament to tune the porbabilities of some simple policies. 

The evolutionary approach has been developed using a tournament approach (a policy play against an other policy) and the fitness function is the number of wins. In this approach if a policy wins against the other it increases the probability of using that policy in the 'official games'.  
## Results
The expert system is the optimale player so it can reach a 100% win ration against a random system and a 50% against another expert system. This means that every time he makes the second move it will win.
The evolutionary algorithm reached quite good results with a 70% win ratio against a random strategy opponent, but it can't win against the expert system.
