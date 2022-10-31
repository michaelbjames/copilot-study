Our replication package details the training task, study tasks, and semi-structured interview questions we used over the course of our grounded theory study.

# Setup
Each participant was given the readme at: `copilot-study/README.md`
They were told to read from the top to the end of the Training Task section.
They then completed the training task.
Once completed, the researcher pointed the participant to their task in the readme.
They worked on their main task until there were 15 minutes left or they finished early.
At that point, the researcher question questions in a semi-structured interview.


# Code
You can find the starting code we gave our participants here.
Participants were given the entire codebase but instructed to only look at their task and to ignore the solution directory if it existed for their task.

Training -> `copilot-study/training/`
Chat Server -> `copilot-study/chat/server_task/`
Chat Client -> `copilot-study/chat/client_task/`
Benford's Law -> `copilot-study/benfords_law/`
Advent of Code -> `copilot-study/advent_of_code/`

## Advent of Code
We had two variants for participants to try as we transitioned to the final task.
We wanted to ensure the last task would not be too hard nor too easy.
So, to find the right balance, we gave one participant the Day 2 and Day 14 of Advent of Code 2021 but Day 2 was too easy, and the task switching wasted our participant's valuable time.
Day 14 ended up being just the right level of difficulty, so all other AOC participants were given only the Day 14 variant.

We lump the tasks together in the paper as both tasks are structurally similar.
Both come with test cases and both have two parts, a parsing and then a manipulation part.

Thusly, you will find under `copilot-study/advent_of_code/python`, both Day 2 and Day 14 files.

# Semi-Structured Interview
When there were 15 minutes left in the session, the researcher moved to a semi-structured interview.
The researcher asked questions specific to the session and had the participant fill in a survey with questions from the file
`Semi-Structured Interview Questions.md`
