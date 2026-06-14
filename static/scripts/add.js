// Add page - handles both sets and individual minifigures
// Server auto-routes fig- numbers to IndividualMinifigure via LOAD_SET / IMPORT_SET
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('[data-add-date="true"]').forEach(el => {
    new Datepicker(el, {
      buttonClass: 'btn',
      format: 'yyyy/mm/dd',
    });
  });

  const addContainer = document.getElementById('add-set');
  if (!addContainer) return;

  new BrickSetSocket(
    'add',
    addContainer.dataset.path,
    addContainer.dataset.namespace,
    {
      COMPLETE: addContainer.dataset.msgComplete,
      FAIL: addContainer.dataset.msgFail,
      IMPORT_SET: addContainer.dataset.msgImportSet,
      LOAD_SET: addContainer.dataset.msgLoadSet,
      PROGRESS: addContainer.dataset.msgProgress,
      SET_LOADED: addContainer.dataset.msgSetLoaded,
      MINIFIGURE_LOADED: addContainer.dataset.msgMinifigureLoaded,
    },
    false,
    false
  );
});
