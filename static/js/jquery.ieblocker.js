
var IElt8 = (navigator.userAgent.indexOf("MSIE 6")>=0)||(navigator.userAgent.indexOf("MSIE 7")>=0) ? true : false;
if(IElt8){

	$(function(){
       
		
		$("<div>")
			.css({
				'position': 'absolute',
				'top': '0px',
				'left': '0px',				
				backgroundColor: 'black',
				'opacity': '0.70',
				'width': '100%',
				'height': $(window).height(),
				 zIndex: 5000
			})
			.appendTo("body");
			
		$('<div class="ie-box"><p><strong>Your browser is no longer supported.</strong></p><p><strong>Please upgrade to a modern browser.</strong></p><p class="browser-links"><a href="http://www.google.com/chrome/index.html" class="browser-link"><img src="http://ias-ess.appspot.com/static/img/browsers/browser_chrome.gif" class="chrome-link"><br />Chrome</a><a href="http://www.mozilla.com/?from=sfx&amp;uid=267821&amp;t=449" class="browser-link"><img src="http://ias-ess.appspot.com/static/img/browsers/browser_firefox.gif" class="firefox-link"><br />FireFox</a><a href="http://www.opera.com/browser/" class="browser-link"><img src="http://ias-ess.appspot.com/static/img/browsers/browser_opera.gif" class="opera-link"> <br />Opera</a><a href="http://www.apple.com/safari/" class="browser-link"><img src="http://ias-ess.appspot.com/static/img/browsers/browser_safari.gif" class="safari-link"><br />Safari</a><a href="http://www.microsoft.com/windows/internet-explorer/default.aspx" class="browser-link"><img src="http://ias-ess.appspot.com/static/img/browsers/browser_ie.gif" class="ie8-link"><br />IE 8 </a></p></div>')
			.css({
				backgroundColor: '#f3f5f2',
				'top': '50%',
				'left': '50%',
				'color': '#D36165',
				marginLeft: -210,
				marginTop: -100,
				width: 'auto',
				padding: 24,
				height: 200,
				'position': 'absolute',
				zIndex: 6000
			})
			.appendTo("body");
	});		
}