# Robotic Warehouse (a sketch)

This is a draft of a robotic warehouse simulator.

# The idea

We want to have a simulated robotis warehouse to be able to compare different kinds of pathfinding
algorithms for robots working in this warehouse. We'll have one type of a robot, occupying
one pixel on a square grid. These robots will be able to move around, carry things, and also
pick them up and store them in both loading/unloading bays and warehouse racks.

The trick of this sketch is that we want be half-way between a more-or-less realistic system design
(with microservices, independent robots, asynchronous communications via a message queue etc.) and
an efficient simulation environment. We also want to be able to run different types of tests,
and compare different types of pathfinding approaches. So we'll aim for something in-between:
some aspects of the system will be radically simplified (like for example, that robots are just
pixels on a grid), while others may look slightly overengineered.

# Architecture overview

The system consists of several units:
1. **GUI** - a front-end, vibe-coded in JS, talking to a flask backend
2. **View** - a flask backend responding to requests from the Visualizer
3. **Universe** - mostly a time-engine. IRL robots would move around on their own and communicate with the orchestrator asynchronously. In this model we have a singleton Physics engine that nudges other players one by one, allowing them to perform certan actions. It's not true concurrency, but for this purpose it's good enough. In practice will work with turns (time ticks), and each turn will take a certain amount of time. During a turn, robots will be given priority in random order. If all of them manage to get processed, great! If not, the turn will be over, and the priority will be passed to system operations (Observer, Scheduler), until a new turn is started.
4. **Orchestrator** - the main logic of the warehouse
5. **Robots** - each robot is an object that interfaces with Physics (on movement and other robot-driven actions) and with the Orchestrator (getting tasks from it, and reporting back)
6. **Strategies** - abstracted pathfinding methods that for a given start and end points calculate a given number of steps in the direction of this point
6. **Observer** - collects diagnostic information about the state of the system
7. **Scheduler** - creates tasks for robots; acts as a (fake) external interface of the warehouse
8. **Strategies** - abstract algorithms that receive information about a required subtask (for now limited to moving from point A to point B) and output some actions for a robot to follow (UDLR movements + wait)

# Running the project

Clone the repo, install as a package with `pip install -e .`.