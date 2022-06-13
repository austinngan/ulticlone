/* Stinky Fingers: Austin Ngan (Gerald), Yoonah Chang (Yelena), Yaying Liang Li (Blob), Han Zhang (Sirap)
SoftDev
P04 -- Ultibase
2022-06-10 */

/*
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
*/

function updateValues() {
  var elements = document.getElementsByClassName("mycheck");
  console.log(elements)
  var names = "";
  for(var i = 0; i < elements.length; i++) {
      if (elements[i].checked == TRUE) {
        names += elements[i];
      }
  }
  document.write(names);
}

document.getElementById("demo").addEventListener("click", updateValues);
