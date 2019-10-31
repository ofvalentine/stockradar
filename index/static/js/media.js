var now = new Date();
var apiDate = "" + now.getUTCFullYear() + (now.getUTCMonth()+1) + now.getUTCDate() + "/" + (now.getUTCHours()+1);
console.log(apiDate);

var width = window.innerWidth;
var height = window.innerHeight;
var xForce, yForce, xStrength, yStrength;

if (width < 321) {
  xForce = width * 0.5;
  xStrength = 0.5;
  yForce = height * 2;
  yStrength = 0.1;
} else if (width < 768) {
  xForce = width * 0.5;
  xStrength = 0.5;
  yForce = height * 1.2;
  yStrength = 0.1;
} else if (width < 1025) {
  xForce = width * 0.5;
  xStrength = 0.1;
  yForce = height * 0.7;
  yStrength = 0.1;
} else if (width < 1367) {
  xForce = width * 0.65;
  xStrength = 0.1;
  yForce = height * 0.5;
  yStrength = 0.1;
} else {
  xForce = width * 0.65;
  xStrength = 0.1;
  yForce = height * 0.5;
  yStrength = 0.3; 
}