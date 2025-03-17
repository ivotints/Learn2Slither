
Install requirements:
    python3 -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt

project about reinforsment learning snake game:

The game board is a 10x10 grid where the snake interacts with apples.
Two green apples and one red apple are randomly placed on the board.
The snake starts at length 3; eating a green apple increases its length, while eating a red apple decreases it.
Colliding with a wall, its own tail, or dropping to zero length results in a game over.
The project requires many training sessions and a graphical interface with configurable display speeds and a step-by-step mode.

Snake Vision: The snake only sees in the four cardinal directions from its head. The state is displayed in the terminal using symbols: W (Wall), H (Snake Head), S (Snake Body), G (Green Apple), R (Red Apple), and 0 (Empty Space). Providing extra information beyond this vision incurs a penalty.
Actions: The agent can take one of four actions—UP, LEFT, DOWN, or RIGHT—based solely on this limited view.
Display: The environment is shown graphically in a window, while the state and actions are output to the terminal.

Rewards: The snake aims to grow to at least 10 cells and survive. Actions are rewarded or penalized (e.g., eating a green apple = positive, red apple = negative, game over = big negative).
Q-learning: The agent uses a Q function (Q-table or Neural Network) to evaluate actions. No other models are allowed.
Training: The agent learns by exploring different actions, receiving rewards, and updating its Q-values iteratively.
Model Saving: The learned state can be saved/exported for future use, and models must be submitted in the git repository.
Evaluation Mode: The agent can run without learning to test a trained model. Graphical and terminal outputs can be disabled to speed up training.

Modular Structure: The program should be well-structured for easy evaluation, with separate modules communicating efficiently.
Submission: Submit the board, agent, and models via Git. Only repository contents will be evaluated.
Models Folder: Include trained models in a chosen file format (e.g., .txt), showing different training stages.
Training: Train multiple models (1, 10, and 100 sessions) to demonstrate learning progress. Training takes time, so prepare in advance.
Evaluation: You must be able to load and test saved models without additional learning to verify performance.
Goal: The snake should reach a length of 10+ and survive as long as possible.

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

create board 10 on 10
each position of the board can have 5 states: Snake Head, body segment, Green apple, Red apple, Empty



Inputs that I would give:
    * Amount of inputs should be fixed for different map size other than 10 (bonus)

    * Distance to left Wall 
    * Distance to right Wall
    * Distance to top Wall
    * Distance to down Wall
    
    * Distance to left closest obstacle (Tail or Wall) 
    * Distance to right closest obstacle (Tail or Wall)
    * Distance to top closest obstacle (Tail or Wall)
    * Distance to down closest obstacle (Tail or Wall)

    * Distance to left Food
    * Distance to right Food
    * Distance to top Food
    * Distance to down Food
    
    * Distance to left Pepper 
    * Distance to right Pepper
    * Distance to top Pepper
    * Distance to down Pepper

    Output:

    * Move Left
    * Move Right
    * Move Up
    * Move Down (can be one neuron with output encoded as 0 - 0.25 - 0.5 - 0.75 - 1, where each range represent Left, Up, Right, Down direction. But better test it in 2 versions. with 4 and 1 neuron)

    # Version 2 just give whole vertical and horisontal lines.
    * Each node (total 19 of them) will get some value like 0 for nothing, 1 for tail, 2 for head, 3 for apple, 4 for pepper.
    This approach will not pass bonus with changing the game area, but should be more smarter snake.

    