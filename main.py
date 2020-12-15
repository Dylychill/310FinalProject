# Dylan McKone
# HCDE 310 Final Project
# Utilizing a base HTML template, this file sets the routes that allow users to input some form data
# that is used to make an API call to DnD5e API (Dungeons and Dragons 5th Edition) and get some information about various DND elements.
# Based on these elements, users can get song recommendations (Spotify API) and chose to save some of the queried data.
# Builds upond previous projects in this course.

from flask import Flask, render_template, request, session
import urllib.parse, urllib.request, urllib.error, json
import os
import logging
app = Flask(__name__)
app.secret_key = os.urandom(24) # for session storage

@app.route("/")
def main_handler():
    app.logger.info("In MainHandler function")
    sessdata = session.get("save-data")
    if sessdata is not None:
        all_saved = json.loads(sessdata)
        return render_template("template.html", saved=all_saved)
    else:
        return render_template("template.html")

@app.route("/gresponse", methods=['GET', 'POST'])
def spell_search_handler():
    # check if user already has save elements
    sessdata = session.get("save-data")
    if sessdata is not None:
        all_saved = json.loads(sessdata)
    else:
        all_saved = [] # each element in this list will be JSON object per spell
    if request.method == 'GET':
        spell = request.args.get("spell") # gets value of this textbox
        # app.logger.info(spell)
        if spell: # form filled out with something
            # make a request for the spell with this variable, then fill in template with returned info
            resp = getSpellInfo(spell) # from API
            if resp:
                return render_template("template.html", spell_info=resp, saved=all_saved)
            else: # no info for that spell returned by API
                return render_template("template.html", no_spells=True, saved=all_saved)
        else:
            return render_template("template.html", no_spells=True, saved=all_saved)
    elif request.method == "POST":
        el = request.form.get("savebtn") # will be the name of the spell
        if el:
            current = {"name":el, "type":"Spell"}
            all_saved.append(current)
            data = json.dumps(all_saved)
            session["save-data"] = data
            return render_template("template.html", saved=all_saved)

# --------Helper Functions below, not routes ----------------

# given the index for the spell to get more info - spell_index is a specific syntax for writing the spell name
# Example url: https://www.dnd5eapi.co/api/spells/acid-arrow/
def getSpellInfo(spell_index):
    fullurl = baseurl + "spells/" + spell_index
    fetched = safeFetch(fullurl)
    if fetched is not None:
        return json.loads(fetched.read())
    else:
        return None


# Helper method to make json a bit more readable, does not alter content
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

# Helper method to safely make requests from nonlocal servers.
# Prints errors when they occur, returns the open url when safe
# when calling this, check for returning none to note errors
def safeFetch(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        print('Error trying to retrieve data: ', e)
        if hasattr(e, "code"):
            print("Error Code: ", e.code)
        elif hasattr(e, "reason"):
            print("Failed to reach the server, Reason: ", e.reason)
        return None

baseurl = "https://www.dnd5eapi.co/api/"

# run it on localhost
if __name__ == "__main__": # if running this file directly
    app.run(host="localhost", port=8080, debug=True) # debug just makes the error messages verbose
