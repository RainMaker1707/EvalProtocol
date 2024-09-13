# Device infected
## Matching URLs
    - /mount/data/file.html
    - /bootstrap/bootstrap.min.js
    - /home.html
    - /null/none.html
    - /static/favicon.png

## Explanations
    - Heartbeat (regular HTTP request using the .js extension) has been detected
    - Kill command detected: an HTTP response containing the data text "kill" has been detected and has been answered with the HTTP request containing a query to '/static/favicon.png'