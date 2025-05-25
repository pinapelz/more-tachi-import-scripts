# How to get token?
As of now, your token doesn't change so once you've followed the steps below once you can re-use it again.
**DO NOT SHARE THIS TOKEN WITH OTHER PEOPLE**

## The easy way
1. Go to AquaDX
2. CTRL+SHIFT+I (Open Dev Tools Panel)
3. Under the `Console` tab, paste the following command
```js
console.log(localStorage.getItem('token'));
```
The output will be your AquaDX token

## The hard way
1. Go to AquaDX
2. CTRL+SHIFT+I (Open Dev Tools panel)
3. Go to Network tab
4. Refresh the page with the Dev Tools Panel Open
5. Search for `/api/v2`
6. Click on any of the requests and check the url. There will be a part of the url that starts with `token=`
7. Copy everything after the `=` up until either the end of the URL or the next `&`

**DO NOT SHARE THIS TOKEN WITH OTHER PEOPLE**
