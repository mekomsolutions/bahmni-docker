jq(function() {
    jq('.close-icon').click(function(e) {
    	var message = jq(this).parent(); 
    	message.fadeOut('slow', function(){ message.find('.text').html(''); });
    });
});
