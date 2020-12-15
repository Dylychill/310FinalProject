# Final Project: My Application
This writeup is for the UW HCDE 310 Final Project, describing primarily `main.py`. The program utilizes 2 APIS, DND 5e API and the Spotify API.

## API Info
### DND 5E
[Link](https://www.dnd5eapi.co/api/)

This API has a lot of information related to Dungeons and Dragons, speficially 5th edition. There's information about spells, monsters, magical items, etc. Predominantly returns with JSON. No authorization is required to access this API.

### Spotify API
[Link](https://developer.spotify.com/documentation/web-api/quick-start/)

The [search](https://developer.spotify.com/documentation/web-api/reference/search/search/) endpoint returns songs based on a search query, providing information Spotify Catalog information on the song, artist, and album. Primarily JSON response. Requires application authorization since this app does not access user information. [Authorization](https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow) requires creating a Spotify developer account and getting client credentials. This means providing the API `/api/token` endpoint with your applications Client ID and Secret Key to get an access token.

## What this program does
Incorporating music into D&D enhances the experience and fun. Music can make an tense situation into a life-or-death decision, can offer insight into an NPCs motives, and set the mood alongside a DM’s (Dungeon Master) exposition. This project with take the form of an interactive webpage where users can pull up information about D&D and get song recommendations that line up with their creations. Users can request information about various spells, monsters, and skills found within 5th Edition and from that gathered information create a search query to find relevant music.
Users can then chose to save that element or song, and the informaion is stored in session storage to persist on next rendering of the page.

## @app.route("/gresponse", methods=['GET', 'POST'])
Adds user information and interaction. This one endpoint is called with both GET and POST methods but perfroms different tasks depending on which. On all occasions, it first searches for any past user information in session and updates the "saved" box.
### GET:
- Makes sure user passed in a param and sends that spell name to the API to get info on that spell. On success adds some details like spell name, damage type (if applicable), and level.
- Some example spell indexes are "bane", "alarm", and "acid-arrow".
- Gives user a button that will save that spell (POST request)
### POST:
- The name of the spell and the type (spell) is put in the "save" box and stored in session storage.
- In future iterations, the type will vary and so it could be type of monster or class.


## @app.route("/")
Primarily landing page for the website that returns a blank, standard page from the template. It looks into session storage for any past user saved data and updates the "save" box with that information.

## static/dnd.css
All the styles are in this static stylesheet.

## templates/template.html
All template html files will be saved in this folder. As of now there is only one which serves as the base for this project.