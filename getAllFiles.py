# A tool to download files from a thread on 4chan.
#
# Use this tool:
# python getAllFiles.py <threadUrl>
#
# The tool should create a subdirectory named after the board and threadId, then
# download the files into this directory. If the tool is run multiple times, it
# should only download the new files. This tool should work for any thread on
# 4chan.
#
# This tool assumes many things:
# - we are using http
# - a thread link contains the substring '/thread/'
# - this '/thread/' is imediately followed by a numerical threadId and preceded
#   by the name of a board, such as 'b' or 'gif'
# - the tool has permission to make files and directories in the CWD
# - all files in the page have a thumbnail with an anchor tag
# - this anchor tag contains both 'class="fileThumb"' and 'href=".*"'
# - all files have unique links
# - there is a filename with an extension in the href link
#
# There may be other assumptions.
#
# author creepymelvindoll, August 18 2015

import sys
import re
import os
import requests

USAGE = "Usage:\npython " + sys.argv[0] + " <threadUrl>\n" +\
    "Call this tool with a threadUrl argument, where threadUrl matches 'http://.*/thread/.*'"

# Check that we have one argument
if len(sys.argv) != 2:
  print USAGE
  print "ERROR: must provide one argument for the 4chan thread URL"
  exit(1)
# Check that it has a valid structure
threadLink = sys.argv[1]
if not re.match(r'http://.*/thread/.*', threadLink):
  print USAGE
  print "ERROR: argument must start with 'http://' and have '/thread/' in it"
  exit(1)

# Get the id of the thread + the board, create a subdirectory by that name
boardId = re.match(r'.*/([^/]+)/thread.*', threadLink).group(1)
threadId = re.match(r'.*thread/(\d+).*', threadLink).group(1)
path = os.getcwd()
threadDir = path + os.sep + boardId + "_" + threadId
if not os.path.exists(threadDir):
  os.makedirs(threadDir)

# Get the contents of the thread, error if we don't get an HTTP 200 response
response = requests.get(threadLink)
if response.status_code != 200:
  if response.status_code == 404:
    print "ERROR: 404, page not found, thread is gone"
  else:
    print "ERROR: got bad status code " + str(response.status_code)
  exit(1)
contents = response.content

# Make a list of all the links in the thread and then download them to threadDir
anchorTags = re.findall(r'<a[^>]*class="fileThumb"[^>]*>', contents)
partialLinks = [re.search(r'href="([^"]*)"', tag).group(1) for tag in anchorTags]
links = ["http:" + partialLink for partialLink in partialLinks]
for link in links:
  fileName = re.match(r'.*/([^/]+$)', link).group(1)
  filePath = threadDir + os.sep + fileName
  count = 0
  if not os.path.exists(filePath):
    print "  downloading " + link + " ..."
    linkFile = requests.get(link)
    with open(filePath, "wb") as download:
      download.write(linkFile.content)
    count += 1
if count == 0:
  print "No files to download"
else:
  print "Downloaded files into " + threadDir
