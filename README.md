MinetestModCleaner
==================

Cleans Minetest mods and mod packs.

* Unzips mod folder (from github or local disk) into working directory
* Removes unnecessary root folders, leaving init.lua or modpack.txt in root folder (ie: modname-master)
* Adds description.txt
* Adds screenshot.png
* Rezips into a new archive
* Returns the achive's location

Please note that this is a work in progress.

License: CC-BY-SA 3.0

Usage
-----

See example.py
