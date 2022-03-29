{-# LANGUAGE TupleSections #-}

module Day14 where

import Data.Function ((&))
import Data.List.Split (splitOn)
import qualified Data.Map as Map

splitParagraphs :: String -> [String]
splitParagraphs = splitOn "\n\n"

-- type definitions
type Rulebook = Map.Map (Char, Char) Char

type State = Map.Map (Char, Char) Int

toState :: String -> State
toState str = foldl (accMap 1) Map.empty (zip str (tail str))

-- parsed input type
type Input = (Char, State, Rulebook)

-- parse string input into input type
parse :: String -> Input
parse input =
  let [template, ruleText] = splitParagraphs input
   in ( head template,
        toState template,
        Map.fromList $ map parseRule $ lines ruleText
      )

parseRule :: String -> ((Char, Char), Char)
parseRule [a, b, _, _, _, _, c] = ((a, b), c)
parseRule _ = error "invalid rule"

applyRule :: Rulebook -> State -> State
applyRule rulebook state =
  let existingPairs = Map.toList state
      newPairs = concatMap (\(pair, count) -> map (,count) $ expandPair rulebook pair) existingPairs
   in foldl (\m (x, n) -> accMap n m x) Map.empty newPairs

expandPair :: Rulebook -> (Char, Char) -> [(Char, Char)]
expandPair rulebook p@(a, b) = case Map.lookup p rulebook of
  Just c -> [(a, c), (c, b)]
  Nothing -> [p]

applyRuleN :: Rulebook -> Int -> State -> State
applyRuleN _ 0 str = str
applyRuleN rulebook n str = applyRuleN rulebook (n - 1) (applyRule rulebook str)

accMap :: Ord a => Int -> Map.Map a Int -> a -> Map.Map a Int
accMap n m x = Map.insertWith (+) x n m

stateToCounts :: Char -> State -> Map.Map Char Int
stateToCounts initialCharacter state =
  state & Map.toList & map (\((a, b), n) -> (b, n)) & foldl (\m (b, n) -> accMap n m b) Map.empty & Map.insertWith (+) initialCharacter 1

-- solve the problem (part A)
solveA :: Input -> Int
solveA (char, template, rulebook) =
  getResult char $ applyRuleN rulebook 10 template

-- solve the problem (part B)
solveB :: Input -> Int
solveB (char, template, rulebook) =
  getResult char $ applyRuleN rulebook 40 template

getResult :: Char -> State -> Int
getResult init state =
  let counts = Map.elems $ stateToCounts init state
   in maximum counts - minimum counts
  
main :: IO ()
main = do
    input <- parse <$> readFile "input.txt"
    print $ solveA input
    print $ solveB input