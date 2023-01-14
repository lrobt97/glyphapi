A probability calculator for glyphs in the game Antimatter Dimensions, written using Flask.

The API currently has three endpoints:

**/threshold**
```
// Request
{
  rarity: The percentage rarity (must be between 0 and 100)
}

// Response
{
  status: Returns the minimum level above which three or four effect glyphs start to appear
}
```

**/rarityProbabilityCalculator**
```
// Request
{
   bonus: Refers to the total percentage rarity added bonus in game
   ru16: Has reality upgrade 16 (Disparity of Rarity) been bought?
   rarity: The target percentage rarity (must be between 0 and 100)
}

// Response
{
  status: Returns the probability of seeing a glyph with the specified rarity, or greater.
}
```


**/effectCountProbabilityCalclulator**
```
// Request
{
   ru17: Has reality upgrade 16 (Duplicity of Potency) been bought?
   rarity: The target percentage rarity (must be between 0 and 100)
   level: The target level of the glyph
   numberOfEffects: The target number of effects
   isEffarig: Is the target glyph type an Effarig glyph?
}

// Response
{
  status: Returns the probability of seeing a glyph with the specified number of effects, given the supplied rarity (does not factor in any logic behind glyph rarity).
}
```
