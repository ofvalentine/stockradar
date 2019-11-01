var keywordsPromise = d3.json('https://stockradar.herokuapp.com/api/keywords/').then(function (data) {

  // SORT DATA FROM API INTO ARRAY OF DICT
  var mostCommon = [];
  var compoundWords = {
    "wells": "fargo",
    "wall": "street",
    "hong": "kong",
    "jp": "morgan"
  };

  Object.entries(data).forEach(([keyword, [frequency, articles]]) => {
    if (keyword in compoundWords) { keyword += " " + compoundWords[keyword]; }
    if (width < 768) { frequency = frequency*0.7; }
    mostCommon.push({ name: keyword, frequency: frequency, articles: articles });
  });

  $(document).ready(function() {
    createBubbles(mostCommon);
  });

  $('#restore-default').click(function() {
    createBubbles(mostCommon);
    $('#changing-text').html("choose topic");
    $('#restore-default').hide();
    $('.topic').hide(300);
    $('#articles-container').hide(300);
    $('#articles-notice-text').show();
    $('html, body').animate({ scrollTop: 0 }, 1000);
    
  });
});