#!/bin/sh

# Install Python runtime at container start
node cli/index.js ppman install python=3.11.4

# Start the Piston API
node index.js
