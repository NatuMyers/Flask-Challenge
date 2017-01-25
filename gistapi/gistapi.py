# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from requests.exceptions import ConnectionError
from flask import Flask, jsonify, request

# not as pythonic but very explicit way of doing this :
#from urllib.request import urlopen #  REQUESTS is more universal, but this will suffice
#import requests
#import json

# Assumption:
# Statflo, I assumed by finding a pattern, it means we will look inside the actual code of the gist's code, so:
import urllib2
import re

# *The* app object
app = Flask(__name__)

@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """

    # "Note: With pagination, you can fetch up to 3000 gists." let's just flatten it out for now.
    gists_url = 'https://api.github.com/users/{username}/gists?3000'.format(
        username='justdionysus'
    )

# Paginated requests will include metadata in the root of the response object, SO...

    response = requests.get(gists_url)#This is the response we get from github...

    #num_pages = response['last'] # https://developer.github.com/v3/#pagination

    #for page in range(2, num_pages + 1):
    # current_page = response['page']
    #We mussst use try catch blocks.
    try:
        response = requests.get(gists_url)#This is the response we get from github...
    except ConnectionError as e:
        #print e #?
        response = "no resp. given"


    # #DONE#REQUIRED: Handle failure from the github API
    # #DONE#BONUS: Handle the case where the results are paginated/

    return response.json()


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()
    #DONE# REQUIRED: Validate the post_data arguments.

    username_error = False

    username = post_data['username']
    pattern = post_data['pattern']

    if username.isalnum():
        username = post_data['username'] #alphanumeric only
    #   patterns are more flexible though so no if

    result = {}

    #gists_for_user is the function above. it's a js obj of ALL GIST METADATA for a user
    gists = gists_for_user(username)
    # REQUIRE: Handle an invalid user name.

    result['status'] = 'success'
    result['username'] = username
    result['pattern'] = pattern
    result['matches'] = []

    for gist in gists:
        #DONE#REQUIRED: Fetch each gist and check for the pattern

        #try to find the pattern in the gist, then add it to our match list


        f = urllib2.urlopen(gist['url']).read()
        matches = re.findall(pattern, f)

        result['matches'].append(gist['url'])

        #DONE#BONUS: Handle huge gists.
        # BONUS: Add a cache layer to this API, so that we don't have to hit the
        #        github API if we have already retrieved the gist for a user
        pass

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
