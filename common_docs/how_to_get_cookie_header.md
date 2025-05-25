**DO NOT SHARE YOUR COOKIES WITH ANYONE, THIS IS THE SAME AS SHARING FULL ACCESS TO YOUR ACCOUNT**

Some scripts require your cookies so it can pull data from sources that require more authentication (such as e-amusement)

# Option 1: Use Cookie-Editor Extension
1. Download the browser extension [Cookie-Editor](cookie-editor.com)
2. Login to the appropriate site to pull your data (see game-specific README)
3. Click on the extension and click `Export`, choose `Header String`

That is your Cookie Header

# Option 2: Use Browser Network Tab (slightly more complicated)
1. Login to the appropriate site to pull your data (see game-specific README)
2. Click on the network tab and search for the current webpage URL in the filter
3. Click on the request to load in the webpage, and find the `Request Headers` section
You should see a section similar to:
```
Cookie: <cookies_here>
```
4. Copy everything after `Cookie:`

That is your Cookie Header
