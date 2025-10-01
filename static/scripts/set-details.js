// Set details page functionality
document.addEventListener('DOMContentLoaded', function() {
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