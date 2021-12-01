# PowerPointGenerator
This project started as a joke, but it quickly took a much bigger turn. PowerPointGenerator is basically a simple programmatic powerpoint file generation python library. Other tools like this exist, but I haven't found any that can generate animations in addition to shapes.

This tool is far from being complete, it can only generate plain colored rectangles and text, and very few animations have been implemented. However, it is more than enough to revisit one of the projects that is dearest to my heart: turing complete systems in PowerPoint.

Now that the generation part is programmatic it is possible to be much more ambitious in the implemented systems and to change their parameters in a few clicks.

## Examples
### Rule110
It is a [1D cellular automaton](https://en.wikipedia.org/wiki/Rule_110) whose rules are determined by one byte. Among the 256 resulting automatons, the "rule 110" is probably the most famous since it has been proven to be Turing Complete. I have recreated this automaton in this slide, the user can define the "rule byte" and the initial state as desired, and then start the generative process by continuously left clicking at a fixed location. Here is "rule 110" with a starting cell in the rightmost position (x20 speed):

![rule110](images/rule110.png)

This slide counts around 1200 shapes and 6100 animations.

### Brainfuck
[Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) is an esoteric programming language known for its minimalism. Indeed, it is composed of only 8 symbols and works with two tapes: one for code, and one for data. I have created in this slide a brainfuck editor and interpreter. The user can write the program he wants (within the limit of characters imposed) and then execute it y continuously left clicking at a fixed location. Here is a "Hello World" program running (x40 speed):

![brainfuck](images/brainfck.png)

This is by far my most complex generated powerpoint with around 2500 shapes and 15000 animations. It is also the most CPU intensive one. To limit the loading time and execution slownest, some modification had to be made:
 - the data tape is not composed of 6 bit cells
 - the output is not ASCII (but 0 to 9, A to Z and followed by spaces)
 - the call stack is finite (depth 3 by default)
But this is only a performance limitation, you can change all these specification in the python script if your computer allows it.
