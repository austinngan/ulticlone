function change() {
    "use strict";
    let vis = document.querySelector('.vis');
    let target = document.getElementById(this.value);
    if (vis !== null) {
    vis.className = 'inv'
    }
    if (target !== null ) {
    target.className = 'vis'
    }
}

document.getElementById('dataType').addEventListener('change', change)
