Of course, the usage of bot is not allowed in any way, and this one has been done for learning purposes only. I strongly advise you against using it.
Some bots are ruining the game for everyone, please do not be part of this, and use this project only with the idea of learning new things.

## Table of Contents
This ReadMe is organized as follows (this is a typical README.md) :
1) [Presentation](#presentation)
2) [Design](#design)
3) [Improvements](#improvements)

## Presentation

This is a small bot that scrap the prices of different resources in the MMORPG Dofus. This is done by reading packets sent by the Auction House (HDV in French).
This is coded mostly in Python, with pyautogui used to interact with the client (and opencv to know how to interact), and scapy used to parse packets received from the server.
Data is stored in an sqlite database using SQLAlchemy. 

As I already had some previous experience with Django, I decided to use SQLAlchemy to store my data, because the very purpose of this project is to learn something new.
The data visualization will be done through a Flask-powered API, and a React.js frontend. I am using this project to learn Flask framework, as I am already familiar with Django, so the code may not be the optimal one.


To parse the messages received from the server, I used some amazing work called [LaBot](https://github.com/louisabraham/LaBot).

The HDV provides a list of categories, and when clicking on it, it displays a list of items.
When clicking on these items, the server sends you a packet with their price for different quantities (1, 10, 100).
Right now, it takes about 30 minutes to get all the data

## Design

I took this project as a good opportunity to learn parallelism, so I tried to split as many things as possible.
Furthermore, it is quite useful for maintenance. 
* If I ever want to switch from Pixel to Socket, I may just have to change one part of my code and get it working.
* If I want to use image recognition instead of reading packets, one change will be enough too.
* If I want to change the way I manage data (e.g. raising alerts), I will change only the "database module".

So I designed this Bot in 3 main modules:
* **mitm**: Sniff the packets received from the server, parses them, and send to the database a dict with all the info
* **database**: Receives dict from **mitm**, generate models and store them
* **pixel**: Uses image recognition to automate the process of clicking on categories/items to have the server sending data to **mitm**

All of these modules expose a class extending a Thread. All this threads communicate.
For example, the mitm uses a Queue to send data to the database.
All of them share a stopping event, so we can gracefully stop an any time.
In the future, the **mitm** may be used to detect bugs, and send Actions to the pixel, that he needs to execute.

### MITM
The MITM is pretty straightforward. It sniffs packets from the connection between the client and the server.
Then, thanks to the protocol decrypted from the source files using [PyDofus](https://github.com/balciseri/PyDofus), it parses the packets.
Once the packets are parsed, we filter them by id (we are only looking for the messages of type *ExchangeTypesItemsExchangerDescriptionForUserMessage*).
Using these packets, we construct dictionnaries with the shape
```python
    item = {
        "category": objectType,
        "item_gid": objectGID,
        "price": itemPrice,
        "quantity": itemQuantity,
    }
``` 
and we send them through a Queue to a Database.

### Database
The database thread continuously reads the queue mentionned previously, and use these packets to create entries in the database.

### Pixel
The pixel bot interacts with the client using image recognition. 
The pixel bot executes "Actions", that are classes containing 2 methods: execute(), that actually does some actions, and a function next_action(),
that returns the Action to execute afterward, depending on what happened during the previous execution.
For example, here the Pixel bot works as follow:
* We start with the HDV window open
* We then check on the left of the screen, containing the category list. using template matching, we find the first unchecked category, and proceed to checkit.
* Then, we scroll all the way down the list of items, and click on them one by one, until we reach the top of the window.
* Once we reached the top of the window, we click on the top item, and scroll one level up, then we start again.
* We do this until scrolling does not change anything (we know this by using image recognition, to see if the item at the top of the window changed or not when we scrolled).
* We scrolling doesn't change anything, we go back to the left of the screen, uncheck the previous category, scroll, and check the next one.
* We do this until we reached the bottom of the categories' list. Then, we scroll all the way up, and start again.

To stop the pixel part, and thus, thanks the stop_event, all the bot, you can just use pyautogui Failsafe and move your mouse to a corner of your screen.

## Improvements
 * Pixel is pretty slow. It is limited by the rendering unit of your computer. For example,
 mine take a while to render all the items of a category, so we are loosing some time. Moreover, the HDV is sometimes a bit buggy, so you have to sleep a lot, which makes the bot quite slow.
 * I originally developed this bot on Mac, and then tried to use it on Windows. There is some fine tuning needed, and some things that I do not explain 
 (for example, pyautogui.scroll(1) will not work on windows, and I have to use pyautogui.scroll(200) instead)
 * There is no way to visualize the data right now. This is quite good because it makes the bot unusable for malicious people.
 * This only works for the resources HDV and not the other ones (like items/creatures/...)
 * We are receiving the same packet twice for every item, and thus currently saving all the data twice.
 * It would be great to be able to filter the data that we are scrapping (maybe we do not care about resources that cost less than 1000K, or we do not care about fish...)