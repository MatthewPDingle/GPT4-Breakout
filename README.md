This was an experiment to see how far I could push GPT-4 (via ChatGPT) towards making a video game.  100% of the code was generated by GPT-4.  I first had it write a design doc for the game before having it attempt to write any code.  Once it had something suitable I had it write the code.  The first version was functional and appeared to have working mechanics, but the paddle and ball speed were way too fast.  Having it adjust those two parameters gave me a playable game.  From there, I asked it to add one feature at a time.  When something didn't work, I explained the anomalous behavior and clarified what was intended.  This was easy and quick work up until around 500 lines of code (breakout004) when I ran into trouble getting it to refactor game-state logic that I needed for another feature I wanted to add next.  This led me down a couple dead-ends before I finally got it to refactor things correctly. From there, progress became slower and more arduous.  GPT-4 was having a hard time remembering the whole codebase and would overlook a lot things when I was asking it to add new features.  I persisted a bit more and then decided to have it write the last 5 levels.  I saved those for last because they're isolated functions that can be understood and written without much context of the entire program.  I asked it how I wanted each level to appear and it could produce them to my spec if I gave it multiple tries and explained fixes.

It would be interesting to repeat the experiment with gpt-4-32k in the API.
