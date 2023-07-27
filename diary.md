# 11/5/2023

## New files

my_drive: A place to locate information locally when I want to do tests on my computer.
local_lms_log.py: Without saving csv files to github. Just to check the html code returned from lms.

## Warning

Better to keep the main branch of github which runs on liara and github and replit. Maybe
in the future we will need it (A time when deta space doesn't exist).

### TODO

* OUTDATED: Another branch on github to store the csv design system (Liara -> Github -> Replit) method

## Discoveries

### ''Show more'' button

Some classes on lms have lots of messages. So there's a button called ''Show more''.
''Show more'' has an attribute called ''rev="next_454183"''.
454183 is the key to load the next messages.
It should be replaced with max_id in this url to fetch the next messages:
"http://lms.ui.ac.ir/widget/index/name/wall.feed?format=html&mode=recent&type=&list_id=0&maxid=458127&subject=group_83713&feedOnly=true"

#### TODO

* 1: Check if the button exists
* 2: Extract the max_id
* 3: Load the webpage and extract information

    Hints: * 1: A good way to solve this could be using a recursiv function, calling itself ALA the button exists
    and appending the results, each time the function returns a new thing.

# 27/5/2023

Did some cleansing.
Can't we just not store cookies locally if each time we're forced to use it?

difference is ok. what about new data after difference
is added?
Now it's ok

need a for loop to iterate over the whole groups.
need to check the functionality of difference for all groups
what happens if data.json hasn't been created?

telegram.py has some problems with making to many lists inside another. it should get the hell right

then action must be scheduled

then recursive message reading

then recusive private message reading
## TODO

1: Find the maximum lifetime of cookies.


# 27/7/2023

i have two option:
1- work with cookies
2- not work with cookied

1- if i work, 


=============
if aio.session.response.history is not none:
    redirect from lms/memebers/home has occured