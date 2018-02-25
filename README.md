# Dominion Physics

## Introduction

This is a project by Tristan Miller ([@tristanlmiller](https://github.com/tristanlmiller/)) from February 2018.  It is intended as a coding refresher in Python and SQL.  The goal is to create simulations showing that the card game *Dominion* contains phase transitions, much like the physical phase transition between liquid and solid.

*Dominion* is a [popular card game](https://boardgamegeek.com/boardgame/36218/dominion) created in 2008.  In *Dominion*, each player has their own deck, and they add/remove cards from their deck over the course of the game.  Each game has a unique set of cards available to be added to players' decks, making the optimal strategy in each game different.  However, there are two archetypical strategies, based on two fundamentally different decks.  The "Big Money" deck makes the best of the 5 cards drawn each turn.  The "Engine" deck includes cards that draw more cards, and tries to draw itself in its entirety each turn.

Because of my background in physics, I recognized that the line between "Big Money" and "Engine" strategies is a phase transition.  More specifically, it's a one-dimensional percolative transition.  That explains why there is such a strong dichotomy between the two strategies over a wide range of conditions.

## Project Outline

1. I created simulations of *Dominion* using Monte Carlo and Markov Chain methods.  The Monte Carlo method generates many random turns and compiles statistics.  The Markov Chain method keeps track of the probabilities of the game being in any particular state.  The simulations are built in a class inheritance structure.
2. The simulation results, and simulation types were recorded in a relational (SQL) database.
3. I retrieved results from the database and created figures to summarize the important points.
4. I wrote an explanation (see below) to contextualize the results.

## Understanding Phase Transitions

### Water

Most people are familiar with the phase transitions in water.  At a certain temperature, water will freeze; at another temperature, water will boil.  The freezing and boiling points also depend on pressure.  This allows us to draw a phase diagram for water.

<div align="center"><img src="/Images/water phase diagram.jpg" alt="Water phase diagram" width=600><br>
<a href="http://www.printablediagram.com/water-phase-diagrams/water-phase-diagram-chemistry/>">Image credit: akitarescueoftulsa.com</a><br></div>
&nbsp;

The phase transitions of water can be thought of as sudden large-scale changes in the properties of water, arising from changes in its microscopic structure.  However, phase transitions are a more general concept that occurs even in pure mathematics.

### Percolation

Here is an example that is more relevant to *Dominion*.  Suppose that we have a network of pipes, with hubs arranged in a 2-dimension grid.  Some adjacent hubs are connected by pipe, and others are not.  If the pipes are arranged randomly, what is the probability that water will be able to flow from point A to point B, in the limit as A and B are infinitely far apart?  

<div align="center"><img src="/Images/bond percolation.png" alt="Bond percolation" width=400><br>
The black lines represent pipes.  <a href="https://en.wikipedia.org/wiki/Percolation_theory#/media/File:Bond_percolation_p_51.png>">Image credit: Wikipedia</a><br></div>
&nbsp;

This is known as the [bond percolation model](https://en.wikipedia.org/w/index.php?title=Percolation_theory&oldid=824236014).  There are two possible scenarios:

**Case 1**: The hubs are broken up into a series of islands, each inaccessible from the others.  Some islands might be very large, but they are still finite in size.  As the distance between A and B goes to infinity, there is zero probability that they are connected on the same island.

**Case 2**: There is at least one infinitely large network of hubs.  Although there will still be some disconnected islands, there is now a nonzero probability that neither A nor B is on an island, and they are connected to each other.

The pipes will very suddenly change from Case 1 to Case 2 as the number of pipes increases.  This is a phase transition.

In reality we will never have an infinite network of pipes.  Nonetheless, phase transitions are good approximations even for small networks of pipes.  There will still be a sudden change where the pipes become a lot more connected.

## The Laboratory Engine

In *Dominion* we are not traversing a network of pipes, but instead traversing from the top of our deck to the bottom.  Analogous to the bond percolation model, I will take the limit as our deck becomes infinitely large.

For our very first example, let's consider a deck composed of two kinds of cards: Copper and Laboratory.

<div align="center"><img src="/Images/copper.jpg" alt="Copper" width=200><img src="/Images/laboratory.jpg" alt="Laboratory" width=200><br></div>

On a typical turn, the player starts with a fresh hand of 5 cards.  During the "Action" phase, the player plays Labs one by one.  Each Lab draws two additional cards.  Once the player is finished playing Labs, they move on to the "Buy" phase.  During this phase, they play all their copper, getting $1 for each one.

In this deck, we can tune one parameter, the fraction of Labs (L).  As a function of L, what is the expected payoff of a single turn?

### Results

Here's what the simulations show.  For L < 1/2, the expected payoff is finite.  For L > 1/2, the payoff is infinite (i.e. it gets larger and larger the longer the simulation runs).  L = 1/2 is the phase transition.

<div align="center"><img src="/Images/lab phase diagram.png" alt="Laboratory phase diagram"></div>

At first, it would seem you can't do any better than infinity.  However, what you can do is increase the probability of drawing infinitely.  I refer to this probability as **Reliability**.

Interestingly, at exactly L = 1/2, the expected payoff is infinite, but the reliability is zero.  However, this only applies to an infinite deck.  In a finite deck, the phase transition is not as sharp, and the payoff is capped by the total payoff in our deck.  The phase transition also occurs slightly earlier (because we draw 5 cards for free).

<div align="center"><img src="/Images/finite lab deck.png" alt="Finite Lab deck"></div>


## The Village/Smithy Engine

For our second example, we will consider a deck composed of three kinds of cards: Copper, Village, and Smithy.

<div align="center"><img src="/Images/copper.jpg" alt="Copper" width=200><img src="/Images/village.jpg" alt="Village" width=200><img src="/Images/smithy.jpg" alt="Smithy" width=200><br></div>

Here, we introduce a new rule.  During the player's Action phase, the player has a limited supply of Actions.  Each Village and Smithy requires an Action to play; if the player runs out of Actions, they must end the phase.  The player starts with only one Action, but can accumulate more Actions if they play Villages (which give +2 Actions).  Each Village draws 1 card when played, and each Smithy draws 3 cards.  During the Buy phase, the player may play any number of Copper without spending any Actions.  In order to have the best turn, it is necessary to mix Villages and Smithies.

Now we have two parameters to tune: the fraction of Smithies (S) and fraction of Villages (V).  The fraction of Copper is 1-S-V.

What is the expected payoff, as a function of S and V?

### Results

Since we have two parameters, I need to show the results as a 2D color map.  For some values of S and V, the expected payoff is finite, which is shown with one color scale.  For other values of S and V, there is a probability of infinite payoff; in these cases I show the reliability with a different color scale.  The diagram is shaped like a triangle because the total number of Villages and Smithies must be less than the number of cards in the deck.

<div align="center"><img src="/Images/village-smithy phase diagram.png" alt="Village/Smithy phase diagram" width=600></div>

Again, we have a phase transition, but it occurs in a 2-dimension space (just like temperature and pressure in the water phase diagram).

## Conclusion

*Dominion* is a game with finite cards, so thinking about infinite decks of cards won't necessarily teach us how to play better.  However, it may help us understand, on a deeper level, why Engine decks are so powerful, and how they fundamentally change the game.