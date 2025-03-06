#!/bin/bash

# Set the URL of the website you want to check
website_url="https://stephen.photography"

# Use wget to recursively download the website and log the output
wget --recursive --spider --no-verbose --output-file=wget_output.log "$website_url"

# Extract and print the broken links from the wget log
broken_links=$(grep -B 2 '404 Not Found' wget_output.log | grep -E '^--' | awk '{print $3}' | sort -u)

# Clean up - remove the wget log file
rm wget_output.log

# Check if there are any broken links
if [ -z "$broken_links" ]; then
    echo "No broken links found."
else
    echo "Broken links found:"
    echo "$broken_links"
fi