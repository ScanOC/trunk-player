// When we're using HTTPS, use WSS too.
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatsock = null;

function start_socket() {
    if(chatsock) {
     chatsock.close();
    }
    
    ws_url = "/ws-calls/scan/default"
    console.log("Connecting ws to " + ws_url);
    chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + ws_url);
    
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);

        if (check_if_rebuild(data)){
          console.log("This call is for us")
	        buildpage();
        }
    };

}

function check_if_rebuild(data) {

      // Check if we are in userscan mode
      pathArray = window.location.pathname.split( '/' );
      pathArray.shift();

      if(pathArray[0] == "scan2" || pathArray[0] == "scan") {
        if (data["scan-groups"].includes(pathArray[1])){
          return true
        }else{
          return false
        }
      }

      if(pathArray[0] == "userscan") {
          if ($('.tg-multi-select').length) {
              tg_array = $('.tg-multi-select').select2("val");
          } else {
              tg_array = null;
          }
          console.log("TG Array is " + tg_array);

          if(tg_array) {
            if (tg_array.includes(data["talkgroup_slug"])){
              return true
            }      
          }else{
            return false;
          }
      }
      return false
};



start_socket();
// {
//   "start_datetime": "2021-09-14 23:48:41+00:00",
//   "audio_file": "3071-1631663321_859462500",
//   "talkgroup_desc": "Troop HQ Disp 1",
//   "talkgroup_slug": "troop-hq-disp-1",
//   "talkgroup_dec_id": "3071",
//   "audio_url": "/audio_files/3071-1631663321_859462500.m4a",
//   "scan-groups": [
//       "all",
//       "un-encrypted"
//   ]
// }