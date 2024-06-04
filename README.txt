##########################################################################

# Idaho Stocking Fishing Analysis Project #

##########################################################################

Purpose of this program is to import and anaylze Idaho's fish and game
website and fish stocking history and schedule, and output the best places to
fish in the state by region.

This is simply a little side project I made for the summer to help me fish
and develop my skills with SQL, Python, and Webscraping



##########################################################################

Functionality

############################################################################

This program initally expects a local SQL server to already be running by
the localhost. Since that it a little out of the scope for this program I 
have not included any code that involves its setup.

The functionality for this is fairly simple:
- We begin by accessing the Idaho Fish and game website and import the
  fish stocking schedule and histories
- Save off this data to SQL for future inspection and manipulation
- For each region and body of water in that region, we analyze how many
  fish have been stocked and when they were stocked. Depending on those two
  variables, give a numerical value representing the fish population. I.E. 
  the body of water's "fishing ranking"

