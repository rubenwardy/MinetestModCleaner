from modmanager import *

# Create cleaner
cleaner = ModManager("working_directory")

# Run on existing mod
# Parameters
# location: path to the archive
# title: the human readable name of the mod
# name: the mod namespace
# (optional) desc: the description to go in description.txt
# (optional) image: the path to the mod image to be copied to screenshot.png
res = cleaner.run("food.zip","Food Mod","food","This is the food mod","")
# returns a CheckResult object

# Get the new zipped archive
res.file

# Check for security risks
if res.safe == 0:
    print("Mod is safe!")
else:
    print("Security risks detected: "+res.safe)

# The same, but gets from github instead of location
res = cleaner.githubGet("https://github.com/rubenwardy/awards","Achievements","awards","This is the award mod","")

# Get messages in HTML format
cleaner.reportHTML()

# Clear messages
cleaner.clear()
