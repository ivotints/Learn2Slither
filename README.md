
Install requirements:
```
    python3 -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
```
project about reinforsment learning snake game:

The game board is a 10x10 grid where the snake interacts with apples.
Two green apples and one red apple are randomly placed on the board.
The snake starts at length 3; eating a green apple increases its length, while eating a red apple decreases it.
Colliding with a wall, its own tail, or dropping to zero length results in a game over.
The project requires many training sessions and a graphical interface with configurable display speeds and a step-by-step mode.

Snake Vision: The snake only sees in the four cardinal directions from its head. Providing extra information beyond this vision incurs a penalty.
Actions: The agent can take one of four actions—UP, LEFT, DOWN, or RIGHT—based solely on this limited view.

Rewards: The snake aims to grow to at least 10 cells and survive. Actions are rewarded or penalized (e.g., eating a green apple = positive, red apple = negative, game over = big negative).
Q-learning: The agent uses a Q function (Q-table or Neural Network) to evaluate actions. No other models are allowed.
Training: The agent learns by exploring different actions, receiving rewards, and updating its Q-values iteratively.
Model Saving: The learned state can be saved/exported for future use.
Evaluation Mode: The agent can run without learning to test a trained model. Graphical and terminal outputs can be disabled to speed up training.

Models Folder: Include trained models in a chosen file format (e.g., .txt), showing different training stages.
```
Snake vision:
          W
          0
          0
          G
          R
          0
          0
          0
W000000000HW
          S
          0
          W

• W = Wall
• H = Snake Head
• S = Snake body segment
• G = Green apple
• R = Red apple
• 0 = Empty space
```
create board 10 on 10
each position of the board can have 5 states: Snake Head, body segment, Green apple, Red apple, Empty



Inputs that I would give:

    * Amount of inputs should be fixed for different map size other than 10 (bonus)

    * Distance to left Wall
    * Distance to top Wall
    * Distance to right Wall
    * Distance to down Wall

    * Distance to left closest obstacle (Tail or Wall)
    * Distance to top closest obstacle (Tail or Wall)
    * Distance to right closest obstacle (Tail or Wall)
    * Distance to down closest obstacle (Tail or Wall)

    * Distance to left Food
    * Distance to top Food
    * Distance to right Food
    * Distance to down Food

    * Distance to left Pepper
    * Distance to top Pepper
    * Distance to right Pepper
    * Distance to down Pepper

    Output:

    * Move Left
    * Move Right
    * Move Up
    * Move Down
