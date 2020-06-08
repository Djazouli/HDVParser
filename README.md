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
Right now, there is no data visualization, but when I decided to continue this project and implement it, I will certainly use the opportunity to discover Flask and a Javascript framework.
But this may be overkill, I have to give it some thoughts.

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

## Improvements
 * Pixel is pretty slow. It is limited by the rendering unit of your computer. For example,
 mine take a while to render all the items of a category, so we are loosing some time. Moreover, the HDV is sometimes a bit buggy, so you have to sleep a lot, which makes the bot quite slow.
 * I originally developed this bot on Mac, and then tried to use it on Windows. There is some fine tuning needed, and some things that I do not explain 
 (for example, pyautogui.scroll(1) will not work on windows, and I have to use pyautogui.scroll(200) instead)
 * There is no way to visualize the data right now. This is quite good because it makes the bot unusable for malicious people.
 * This only works for the resources HDV and not the other ones (like items/creatures/...)
 * We are receiving the same packet twice for every item, and thus currently saving all the data twice.
 * It would be great to be able to filter the data that we are scrapping (maybe we do not care about resources that cost less than 1000K, or we do not care about fish...)