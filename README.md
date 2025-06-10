# Robotic Warehouse: a sketch

This is a draft of a robotic warehouse simulator.

# The idea

We want to have a simulated robotic warehouse to be able to compare different kinds of pathfinding algorithms for robots working in this warehouse. We have one type of a robot, occupying one pixel on a square grid. These robots can to move around, carry items, and pick and store in both loading/unloading bays and warehouse racks.

The trick of this sketch is that we want to be half-way between a more-or-less realistic system design (with microservices, independent robots, asynchronous communications via message queues and stacks etc.) and a (relatively) efficient simulation environment. We also want to be able to run tests, and compare different pathfinding approaches. So we'll aim for something in-between:
some aspects of the system will be radically simplified (like for example, that robots are just
pixels on a grid), while others may look slightly overengineered.

# Running the project

Clone the repo. Run `/src/robowh/main.py`. In a browser, run `http://localhost:5000/`.

To mess with the stuff, clone and install it as a package with `pip install -e .`.

# Architecture overview

The system consists of several units:
1. **GUI** - a front-end, vibe-coded in JS, talking to a flask backend
2. **View** - a flask backend responding to requests from the Visualizer
3. **Universe** - mostly a time-engine. IRL robots would move around on their own and communicate with the orchestrator asynchronously. In this model we have a singleton Universe engine that nudges other players (both microservices and robots) one by one, allowing them to perform certan actions. It's not true concurrency, but for this purpose it's good enough. In practice we will work with turns (time ticks), and each turn will take a fixed amount of time. During a turn, robots will be given priority in random order. If all of them manage to get processed, great! If not, the turn will be over, and the priority will be passed to system operations (Observer, Scheduler), until a new turn is started.
4. **Orchestrator** - the main logic of the warehouse: coordinating storage locations, assigning tasks to robots. IRL would receive orders from the Scheduler (but we have a short-cut here, and just move random stuff around all the time).
5. **Robots** - each robot is an object that interfaces with Universe (on movement and other robot-driven actions) and with the Orchestrator (getting tasks from it, and reporting back)
6. **Strategies** - abstracted pathfinding methods that for a given start and end points calculate a given number of steps in the direction of this point
6. **Observer** - collects diagnostic information about the state of the system
7. **Scheduler** - Acts as an external interface of the warehouse. Not really used in this project.
8. **Strategies** - abstract algorithms that receive information about a required subtask (for now limited to moving from point A to point B) and output some actions for a robot to follow (UDLR movements + wait)

The ontology of behaviors:
* Orders - normally would come "from the exernal world" and placed in a queue by the Scheduler. In a model one would probably expect the Scheduler to generate fake orders. But in this model, for now, Scheduler is an empty shell, and tasks are generated directly by the Ochestrator.
* Tasks - are assigned to robots by the Orchestrator. IRL Orchestrator would read them from a queue populated by scheduler. In this model, the Ochestrator generates tasks itself (at least for now).
* Actions - most tasks consist of several actions, a typical task for a typical robot is broken into at least 4 tasks: come to A, pick an order, move to B, drop an order.
* A queue of planned next moves - a part of a planned motion, generated for an action by a staregy
* Individual move

One weird semantic issue is that movements of robots may happen at several different levels of organization. We may want to just move robots around to resolve bottlenecks; movements come up during task execution, as parts of it; and then movement is planned, and finally elementary movements on the grid are happening as well. Let's use different words for this. It's not an ideal list of course, but better than nothing haha:
* A task that is movement-only we will call `reposition`
* An action within a task that is about moving from A to B we'll call `go`
* A sequence of next elementary steps we'll call `next_moves`
* Finally, elementary moves we'll call `move`

# Next steps

TODO:
* We have an idling bug currently that locks the WH with some probability. Make "idling" about picking a point at random, not near a rack, and going to it. I even tried to code it, but it seems that robots that are blocking the bays before the warehouse dies are not finishing their tasks, so they never "report for service", and never relocate. Can it be that modified A-star fails when initiated right next to the goal in some weird way? Or are they failing to unload their load for some other weird reason?
* Count the number of robots that were processed (didn't time out), show it in the console
* Add n tasks processed per second
* Measure and report confusins and blockage for robots, percent of time blocked
* Add buttons for adding robots and removing robots
* Improve unit test for robots, as towards the end it seems to be making strange assumptions
* Make "confused" element in UI actually report the number of confused robots

Nice to haves:
* Move orders creation logic to the scheduler?
* Make robots remember what they carry (or None), and check that at loading/unloading
* Unit tests for shelves utility functions (locking, random elements)
* Unit test for Universe `.scan()`
* Revise the singleton situation. The handling of sigletons is still a bit awkward: Universe is the only true singleton, and it creates others, except for the viewer, that is created in the main script. But also, to most (except for robots), universe is passed as a parameter, while for robots we break circular references using a deferred import (ugly). How to best standardize this? Should we always pass a reference to the universe explicitly at object creation, or is there a better way?