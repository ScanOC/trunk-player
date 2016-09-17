// When we're using HTTPS, use WSS too.
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatsock = null;

function start_socket() {
    if(chatsock) {
     chatsock.close();
    }
    // Check if we are in userscan mode
    pathArray = window.location.pathname.split( '/' );
    pathArray.shift();
    ws_url = "/ws-calls" + window.location.pathname;
    if(pathArray[0] == "userscan") {
        // Build TGs from select box
        console.log("In WS connect for userscan");
        tg_array = $('.tg-multi-select').select2("val");
        console.log("TG Array is " + tg_array);
        if(tg_array) {
          ws_url =  "/ws-calls/tg/" + tg_array.join('+');
        } else {
          return false;
        }
    }
    console.log("Connecting ws to " + ws_url);
    chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + ws_url);
    
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
	buildpage();
    };

}

start_socket();
