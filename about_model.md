# What makes model unique?
* safe random actions
* State: obst0/1|apple0/1|pepper0/1|norm_distance0-1 x 4

Gorynych_v1.2:
* Model will stop training if agent do not improve in next 500 steps.
* added evaluation.txt file with summary of evaluations

Gorynych_v1.3:
* possible to choose amount of neurons as arguments
* 128-64 neurons

Gorynych_v1.4
* Lobby added.

Gorynych_v1.5
* only 12 neurons input, no pepper, no punishment for pepper.
* model safe and evaluation every 10 steps
* 64 training batch