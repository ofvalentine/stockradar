// ANIMATE SCROLL TO TOP
$(window).scroll(function() {
  if ($(this).scrollTop() >= 50) { $('#scroll-top').fadeIn(200); }
  else { $('#scroll-top').fadeOut(200); }
});

$('#scroll-top').click(function() {
  $('body,html').animate({ scrollTop : 0 }, 500);
});