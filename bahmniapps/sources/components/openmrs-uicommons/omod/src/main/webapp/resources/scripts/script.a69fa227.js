$(document).ready(function() {
	$('#menu-list').scrollspy();
	$('#menu-list.nav > li').removeClass('active');
  if(window.location.hash == "") {
    $('#menu-list.nav > li:first').addClass('active');
  }

	$(window).scroll(function() {
  	if ($(this).scrollTop() > 130) {
    	$('#menu-container').css('position', 'fixed').css('top', 0);
    	$('#content').css('margin-left', '254px');
  	} else {
    	$('#menu-container').css('position', 'relative');
    	$('#content').css('margin-left', '0px');
  	}
	}); 

  var options = { source: ["Antepartum Ward", "Central Archives", "Clinic Registration", "Community Health", "Dental", "Emergency", "Emergency Reception", "ICU", "Isolation", "Labor and Delivery", "Main Laboratory", "Men's Internal Medicine", "NICU", "Operating Rooms", "Outpatient Clinic", "Pediatrics", "Post-op GYN", "Postpartum Ward", "Pre-op/PACU", "Radiology", "Surgical Ward", "Women's Clinic", "Women's Internal Medicine", "Women's Outpatient Laboratory", "Women's Triage"], items: 3 };
  $('#typeahead').typeahead(options);
});