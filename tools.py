'''
Purpose: Misc. tools for testing purposes.
'''

import polars as pl

# Write a basic csv file
length = 1000
pl.DataFrame({
    'a' : [n for n in range(length)],
    'b' : [n*2 for n in range(length)],
    'c' : [n**2 for n in range(length)],
    'd' : [n**3 for n in range(length)]
}).write_csv('.\\data\\demo.csv')

