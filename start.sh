#!/bin/sh

# Install Python runtime (only runs when container starts)
node cli/index.js ppman install python=3.11.4

# Start the Piston API
node index.js
