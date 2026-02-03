FROM ghcr.io/engineer-man/piston/api:latest

EXPOSE 5000

# Copy the start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Use the start script as the container entrypoint
CMD ["/start.sh"]
