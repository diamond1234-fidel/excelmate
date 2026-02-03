# Use official Piston API image
FROM ghcr.io/engineer-man/piston/api:latest

# Expose port for Railway
EXPOSE 5000

# Optional: install Python runtime on startup
# Replace 3.11.4 with the version you want
RUN ["cli/index.js", "ppman", "install", "python=3.11.4"]

# Start the Piston API
CMD ["node", "index.js"]
