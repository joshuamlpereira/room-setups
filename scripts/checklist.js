(function () {
  var sheets = document.querySelectorAll('.sheet');
  function setZoom(z) {
    for (var i = 0; i < sheets.length; i++) sheets[i].style.zoom = z;
  }
  function fit() {   // shrink the letter pages to fit small screens
    var w = document.documentElement.clientWidth;
    var z = Math.min(1, (w - 24) / 816);
    setZoom(z < 1 ? String(z) : '');
  }
  window.addEventListener('resize', fit);
  window.addEventListener('beforeprint', function () { setZoom(''); });
  window.addEventListener('afterprint', fit);
  fit();
  document.getElementById('print').addEventListener('click', function () { window.print(); });
  document.getElementById('clear').addEventListener('click', function () {
    var boxes = document.querySelectorAll('input[type=checkbox]');
    for (var i = 0; i < boxes.length; i++) boxes[i].checked = false;
  });
})();
