% rules.pl

% FIXME: does not take hybrid mana into account
red(Card) :- cost(Card, Cost), member(red, Cost).
blue(Card) :- cost(Card, Cost), member(blue, Cost).
black(Card) :- cost(Card, Cost), member(black, Cost).
green(Card) :- cost(Card, Cost), member(green, Cost).
white(Card) :- cost(Card, Cost), member(white, Cost).

% TODO: colorless, gold

/*** converted mana cost ***/

cmc([], 0).

% cost starts with a color
cmc([H|T], N) :-
    member(H, [red, green, blue, white, black]),
    cmc(T, N2),
    N is N2 + 1, !.

% cost starts with a number
cmc([H|T], N) :-
    number(H),
    cmc(T, N2),
    N is H + N2, !.

% anything else (like X)
cmc([H|T], N) :-
    cmc(T, N).

converted_mana_cost(Card, CMC) :-
    cost(Card, C),
    cmc(C, CMC).

