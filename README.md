# Dominion Physics

## Introduction

This is a project by Tristan Miller ([@tristanlmiller](https://github.com/tristanlmiller/)).  It is intended as a coding refresher in Python and SQL.  The goal is to create simulations showing that the card game *Dominion* contains phase transitions, much like the physical phase transition between liquid and solid.

*Dominion* is a [popular card game](https://boardgamegeek.com/boardgame/36218/dominion) created in 2008.  In *Dominion*, each player has their own deck, and they add/remove cards from their deck over the course of the game.  Each game has a unique set of cards available to be added to players' decks, making the optimal strategy in each game different.  However, there are two archetypical strategies, based on two fundamentally different decks.  The "Big Money" deck makes the best of the 5 cards drawn (by default) each turn.  The "Engine" deck tries to draw itself in its entirety, each turn.

With my background in physics, I recognized that the line between "Big Money" and "Engine" strategies is a phase transition.  More specifically, it's a one-dimensional percolative transition.  This explains why there is such a strong dichotomy between the two strategies over a wide range of conditions.

## Project Outline

1. I created simulations of *Dominion* using Monte Carlo and Markov Chain methods.  The Monte Carlo method generates many random turns and compiles statistics.  The Markov Chain method keeps track of the probabilities of the game being in any particular state. (See my workspace at "Dominion simulations.ipynb")
2. The different kinds of simulations each correspond to a different class, some classes inheriting others.
3. The simulation results, and simulation types are recorded in a relational (SQL) database.
4. I retrieve results from the database and create figures to summarize them.
5. I contextualize and summarize the results (See below).

## Understanding Phase Transitions

#### Water

Most people are familiar with the phase transitions in water.  At a certain temperature, water will freeze; at another temperature, water will boil.  The freezing and boiling points also depend on pressure.  This allows us to draw a phase diagram for water.

<div align="center"><img src="/Images/water phase diagram.jpg" alt="Water phase diagram" width=600><br>
<a href="http://www.printablediagram.com/water-phase-diagrams/water-phase-diagram-chemistry/>">Image credit: akitarescueoftulsa.com</a><br></div>
&nbsp;

The phase transitions of water can be thought of as sudden large-scale changes in the properties of water, arising from changes in its microscopic structure.  However, phase transitions are a more general concept, occurring even in pure mathematics.

#### Percolation

One relevant example, is the [bond percolation model](https://en.wikipedia.org/w/index.php?title=Percolation_theory&oldid=824236014).  Suppose that we have a network of pipes in a 2-dimension grid.  Some percentage of pipes allow water through (black lines below) and the rest do not.  If the pipes are arranged randomly, what is the probability that water will be able to flow from point A to point B?  

<div align="center"><img src="/Images/bond percolation.png" alt="Bond percolation" width=400><br>
<a href="https://en.wikipedia.org/wiki/Percolation_theory#/media/File:Bond_percolation_p_51.png>">Image credit: Wikipedia</a><br></div>
&nbsp;

More specifically, we are interested in the limit as the distance between A and B goes to infinity.  This leads to two possible scenarios:
**Case 1**: The pipes are broken up into a series of islands, each inaccessible from the others.  Some islands might be very large, but they are still finite in size.  As the distance between A and B goes to infinity, there is zero probability that they are connected on the same island.
**Case 2**: There is at least one network of pipes that is infinite in extent.  Although there will still be some disconnected islands of pipes, there is now a nonzero probability that both A and B will be connected by the infinite network.

As it turns out, we have Case 2 when the fraction of pipes exceeds 50%.  Otherwise, we have Case 1.  This sudden change in behavior is what we call a phase transition.

Although we take a mathematical limit, any real physical system will contain only a finite number of atoms.  Likewise, a deck of cards contains only a finite number of cards.  Nonetheless, phase transitions tend to be a very close approximation of reality, even when we talk about very small numbers.


## Phase transitions in *Dominion*

For our very first example of a phase transition in *Dominion*, we will consider a simple deck composed of only two kinds of cards: Copper and Laboratory.

<div align="center"><img src="/Images/copper.jpg" alt="Copper" width=200><img src="/Images/laboratory.jpg" alt="Laboratory" width=200><br></div>

On a typical turn, the player starts with a fresh hand of 5 cards.  During the "Action" phase, the player plays Labs one by one.  Each Lab draws two additional cards.  Once the player is finished playing Labs, they move on to the "Buy" phase.  During this phase, they play all their copper, getting $1 for each one.

Since we are trying to think of this in terms of phase transitions, let's imagine that the size of the deck approaches infinity.  I use L to refer to the fraction of Labs in the deck.  The fraction of Copper is 1-L.

What is the expected payoff of a single turn?

#### Results

The general result is that there is a phase transition at L = 1/2.  For L < 1/2 (the "Big Money" phase), the expected payoff is finite.  For L > 1/2 (the "Engine" phase), the expected payoff is infinite, because there is a finite probability of drawing the whole deck.  So instead of characterizing the engine phase by the expected payoff, we characterize it by "Reliability", which is the probability of drawing the whole deck.

[TBA]

## The Village/Smithy Engine

For our second example, we will consider a deck composed of three kinds of cards: Copper, Village, and Smithy.

<div align="center"><img src="/Images/village.jpg" alt="Village" width=200><img src="/Images/smithy.jpg" alt="Smithy" width=200><br></div>

Here, we introduce a new rule.  During the player's Action phase, the player has a limited supply of Actions.  Each Village and Smithy requires an Action to play; if the player runs out of Actions, they must end the phase.  The player starts with only one Action, but can accumulate more Actions if they play Villages (which give +2 Actions).  Each Village draws 1 card when played, and each Smithy draws 3 cards.  During the Buy phase, the player may play any number of Copper without spending any Actions.

This example is more complicated than the Laboratory deck, because now we have two parameters to consider.  V is the fraction of Villages in the deck, while S is the fraction of Smithies.  The fraction of Copper is 1-S-V.

What is the expected payoff, as a function of S and V?

#### Results

Again, we have a phase transition, with the expected payoff being infinite for certain values of S and V.  We can show the location of this phase transition with a 2-d phase diagram, much like the one we showed for water.  (The phase diagram is shaped like a triangle because of constraints on S and V.)

[TBA]