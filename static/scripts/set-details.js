// Set details page functionality
document.addEventListener('DOMContentLoaded', function() {
  // Background market-value refresh (SIDECAR_AUTO_FETCH_PRICE): the page
  // renders with cached values, then this swaps in the TTL-refreshed price
  // card so the BrickLink scrape never blocks the page load.
  const priceCard = document.getElementById('sidecar-price-card');
  if (priceCard && priceCard.dataset.priceSrc) {
    fetch(priceCard.dataset.priceSrc)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Response status: ${response.status}`);
        }
        return response.text();
      })
      .then(html => { priceCard.innerHTML = html; })
      .catch(error => console.log(error.message));
  }

  const collapseElement = document.getElementById('all-instances');
  const toggleIcon = document.getElementById('copies-toggle-icon');

  if (collapseElement && toggleIcon) {
    collapseElement.addEventListener('shown.bs.collapse', function() {
      toggleIcon.className = 'ri-arrow-up-s-line fs-4';
    });

    collapseElement.addEventListener('hidden.bs.collapse', function() {
      toggleIcon.className = 'ri-arrow-down-s-line fs-4';
    });
  }
});