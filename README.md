<img src="static/brick.png" height="100" width="100">

# BrickTracker

A web application for organizing and tracking LEGO sets, parts, and minifigures. Uses the Rebrickable API to fetch LEGO data and allows users to track missing pieces and collection status.

<a href="https://www.buymeacoffee.com/frederikb" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="41" width="174"></a>

<div id="donate-button-container">
<div id="donate-button"></div>
<script src="https://www.paypalobjects.com/donate/sdk/donate-sdk.js" charset="UTF-8"></script>
<script>
PayPal.Donation.Button({
env:'production',
hosted_button_id:'48JEEKLCGB8DJ',
image: {
src:'https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif',
alt:'Donate with PayPal button',
title:'PayPal - The safer, easier way to pay online!',
}
}).render('#donate-button');
</script>
</div>


## Features

- Track multiple LEGO sets with their parts and minifigures
- Mark sets as checked/collected
- Mark minifigures as collected for a set
- Track missing pieces
- View parts inventory across sets
- View minifigures across sets
- Wishlist to keep track of what to buy

## Prefered setup: pre-build docker image

See [Quick Start](https://bricktracker.baerentsen.space/quick-start) to get up and running right away.

See [Walk Through](https://bricktracker.baerentsen.space/tutorial-first-steps) for a more detailed guide.

## Documentation

Most of the pages should be self explanatory to use.
However, you can find more specific documentation in the [documentation](https://bricktracker.baerentsen.space/whatis).

You can find screenshots of the application in the [overview](https://bricktracker.baerentsen.space/overview) documentation.
