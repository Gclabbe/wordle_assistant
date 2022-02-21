# wordle_assistant
Playing with code and some basic word theory to assist in guesses for the NYT Wordle game

## Overview
In the never ending pursuit of coding strength and efficiency, sometimes seemingly simple tasks
become a great exercise to remember the basics.

There is nothing exciting in this code.  It establishes a class that represents a game and then takes
in feedback from the game to create a smaller and smaller list of options for the next guess towards
finding the final word in the puzzle.

This is done purely for fun and to play a bit with some word theory (very basic right now).  Maybe
eventually moving towards a prediction of scores for each possible word using a nearest-neighbors
approach on cascading letter combinations.

Or other ideas on how such a simple game could be over-engineered in the search for automated solutions :)

## Setting up the game
There really is nothing to it.  Start a game.  No settings:
> game = wordle_game()

Then pass it a corpus of words that are stored in a csv file as "word", "count".  And tell the game
to prpare the data:
> game.load_data(folder, filename)  
> game.prep_data()

Now, if you want to see what the system recommends as the best options for your first word:
> game.recommend_next()

See below for some details on options and theory for this function

## Round 1 -- best start word
So, many theories out there.  Pick one.  

Here, the assumption is pretty simple.  Based on this corpus of 333K words, and using the scoring system
described below, what are the top potential words ... i.o.w. what words have the most unique high-frequency
letters.  To date, success has come from using:
* their
* email
* about

In each of those cases the words have several high frequency letters, are very common in the original
corpus and have no duplicate letters, giving us the maximum feedback.

## Interpret the results and guess at next word
Now that you've input the first word, Wordle will give a visual response to the fitness of each letter.
* green -- this letter is correctly placed
* yellow -- this letter is in the word (at least one time), however, not at this position
* gray -- this letter is not in the word

For the setup of the next round we need this information.  In order to make it a bit easier to enter, the
results use letter codes to represent the feedback:
* c -- correct placement
* y -- good letter, wrong placement
* x -- bad letter

A word (email) that gets feedback from wordle as:
* green, gray, gray, yellow, gray

would be entered into the game as:
> game.next_round('email', 'cxxyx', round_num=1)

The system will then build a new corpus based on this feedback and make new suggestions for the next word.

## Updates
v0.00:  2/21/2022) Initial check-in and some basic documentation

## Ideas
* Keep track of each word / feedback combo from each round
* Save output on winning round
    * Date
    * Word X entry / feedback
* Save running score tally    

## How does recommend_next work?
Parameters that can be passed to recommend_next
* options (int=50) -- how many of the words in the corpus to examine
* display (int=10) -- how many of the top scoring words to show
* allow_dupe_letters (bool=True) -- if False, remove any word with the same letter twice or more

The basic idea is to use word and letter frequency to identify the words with the most information about
the solution.

All letters for all remaining words are counted and summed.  Then for each word an initial score is created
that is the sum of the count values of each letter in that word.

This score is then multiplied by the probability of this particular word from the original corpus, resulting
in a final score.

As a simple example:  

    corpus_words = ['apple', 'orange', 'pear']
    probability = [0.10, 0.05, 0.01]
    letter_freq = {'a': 3, 'e': 3, 'g': 1, 'l': 1, 'n': 1, 'o': 1, 'p': 3, 'r': 2}

    apple_score = (3 + 3 + 3 + 1 + 3) * 0.1 = 1.3
    orange_score = (1 + 2 + 3 + 1 + 1 + 3) * 0.05 = 0.45
    pear_score = (3 + 3 + 3 + 2) * 0.01 = .11

So, apple is the most likely to be the next best guess.  

However, if allow_dupe_letters is set to False, apple will get a score of 0 and orange becomes the top
next choice.  

Why would you do this?  The theory is that in the early rounds we want to most information about what letters
are and are not in the final word.  Inputting as many unique letters as possible will have a dramatic impact
on reducing the body of words to explore for continued recommendations.