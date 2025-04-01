# What makes model unique?
* safe random actions
* nuerons 16-32-16-4
* State: obst0/1|apple0/1|pepper0/1|norm_distance0-1 x 4

v1.1:
* get_action_half_safe (90% chance of safe move while exploring)

Settings:
INPUT_SIZE = 16
OUTPUT_SIZE = 4
BATCH_SIZE = 128
EPSILON_DECAY = 0.9998
MEMORY_LEN = 10000
FIRST_NEURON_LAYER = 32
SECONS_NEURON_LAYER = 16
