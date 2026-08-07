// First-run telemetry splash. Only loaded when the server has decided the
// splash should show (see inject_telemetry() in bricktracker/app.py), so no
// extra visibility check is needed here.
document.addEventListener('DOMContentLoaded', function() {
  const modalElement = document.getElementById('telemetrySplashModal');
  if (!modalElement) {
    return;
  }

  const modal = new bootstrap.Modal(modalElement);
  modal.show();

  function sendConsent(choice) {
    fetch(`/admin/api/telemetry/consent/${choice}`, { method: 'POST' })
      .then(() => modal.hide())
      .catch(error => {
        console.error('Telemetry consent error:', error);
        modal.hide();
      });
  }

  const enableBtn = document.getElementById('telemetry-splash-enable');
  if (enableBtn) {
    enableBtn.addEventListener('click', () => sendConsent('enable'));
  }

  const disableBtn = document.getElementById('telemetry-splash-disable');
  if (disableBtn) {
    disableBtn.addEventListener('click', () => sendConsent('disable'));
  }
});
