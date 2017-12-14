{-# OPTIONS_GHC -F -pgmF htfpp #-}
-- ddrescueprint.hs - console version of ddrescueview (sort-of)
import Text.ParserCombinators.Parsec
import Control.Monad (void)
import Numeric (readHex)
import Data.List (intercalate)

import Test.Framework

default_bsize = 2048
default_width = 80

-- ddrescueview log characters
goodBlock = '+'
badBlocks = "*/-"
nonTried  = '?'
statusChars = "?*/-FG+"
blockStatusChars = goodBlock : '?' : badBlocks

comment :: Parser (Maybe (Int,Int,Char))
comment = do
    char '#'
    manyTill anyChar (try $ char '\n')
    return Nothing <?> "comment"

prefixedHexNum :: Parser Int
prefixedHexNum = do
    string "0x"
    a <- many1 hexDigit
    return (fst $ head $ readHex a) <?> "prefixedHexNum"

currentpos :: Parser (Maybe (Int,Int,Char))
currentpos = do
    prefixedHexNum
    spaces
    oneOf statusChars
    return Nothing <?> "currentpos"

rangeline :: Parser (Maybe (Int,Int,Char))
rangeline = do
    a <- prefixedHexNum
    spaces
    b <- prefixedHexNum
    spaces
    c <- oneOf blockStatusChars
    return (Just (a,b,c)) <?> "rangeline"

logline :: Parser (Maybe (Int,Int,Char))
logline = try comment <|> try currentpos <|> rangeline

loglines :: Parser [Maybe (Int,Int,Char)]
loglines = logline `sepBy` (char '\n')

{-----------------------------------------------------------------------------
 - test strings and assertions
 -----------------------------------------------------------------------------}

goodstr1 = "0x05010000     ?\n#      pos        size  status\n0x00000000  0x05010000  +"
example_comment = "# asdasd"
good_hexnum = "0x05010000"
good_currentpos = "0x05010000     ?"
good_rangeline = "0x00000000  0x05010000  +"
good_rangeline_data = Just (0, 0x05010000, '+')
another_rangeline = "0x05010000  0x184DC000  ?"
another_rangeline_data = Just(0x05010000, 0x184DC000, '?')

--myparse a b = parse a "" b
--test_good_currentpos = assertBool $ (myparse currentpos good_currentpos) == Right Nothing
--myparse2 a b c = assertBool $ (parse a "" b) == c
--test_good_currentpos = myparse2 currentpos good_currentpos (Right Nothing)

test_good_currentpos = assertBool $ (parse currentpos "" good_currentpos) == Right Nothing
test_good_rangeline = assertBool $ (parse rangeline "" good_rangeline) == Right good_rangeline_data
test_good_logline = assertBool $ (parse logline "" good_rangeline) == Right good_rangeline_data
test_good_both = assertBool $ (parse loglines "" (good_currentpos ++ "\n" ++ good_rangeline)) == Right [ Nothing , good_rangeline_data ]

test_goodstr1 = assertBool $ (parse loglines "" goodstr1) == Right [ good_rangeline_data ]

-- XXX: a prop/assert that size `mod` bsize == 0 always?
-- turns a parsed range line into a stream of status chars, one per block
flatten :: Int -> (Int,Int,Char) -> [Char]
flatten bsize (_,size,c) = take chunk (repeat c)
    where chunk = size `div` bsize

-- take a stream of characters, and intersperse a newline every x chars
splitlines :: Int -> [Char] -> [Char]
splitlines _ "" = ""
splitlines length stream = intercalate "\n" [head, splitlines length tail]
    where (head, tail) = splitAt length stream

-- test main method...
main = htfMain htf_thisModulesTests
