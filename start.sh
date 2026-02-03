#!/bin/sh

# Install Python if not installed
node cli/index.js ppman install python=3.11.4

# Optional: install packages like Pandas
node cli/index.js ppman install python=3.11.4 pip
python3 -m pip install pandas openpyxl

# Start the API
node index.js
