active_play=0;
buildpage_running = 0;
currently_playing=0;
last_call = 0;
page_title = 'ScanOC';
first_load = 1;
first_play = 1;
seen = [];
curr_id_list = [];
curr_file_list = [];
curr_tg_list = [];
var force_page_rebuild = 0;
var base_api_url = "/api_v1/";
//var url_params = document.location.search
//var api_url = base_api_url + "/scanlist/default/";
//var pathArray = window.location.pathname.split( '/' );
// leading slash (/) causes a blank first object
//pathArray.shift();
//api_url = base_api_url + pathArray.join('/');
//if(url_params) {
//  api_url = api_url + url_params
//
var api_url = null;
var url_params = null;

var buildpage_running = 0;

function update_scan_list() {
    start_socket();   
    buildpage();
}

function update_api_url() {
    url_params = document.location.search
    pathArray = window.location.pathname.split( '/' );
    pathArray.shift();
    console.log("url build");
    if(pathArray[0] == "userscan") {
        // Build TGs from select box
        console.log("In userscan url build");
        tg_array = $('.tg-multi-select').select2("val")
        if(tg_array) {
          api_url = base_api_url + "tg/" + tg_array.join('+');
          console.log("New API url " + api_url)
        } else {
          api_url = null;
        }
    } else {
        api_url = base_api_url + pathArray.join('/');
    }
    if(api_url && url_params) {
        api_url = api_url + url_params
    }
    //start_socket(); // reconnect with new talkgroups
}

function url_change(new_url) {
    clearpage();
    // Simple funcation to change url and rebuild the page
    var stateObj = { foo: "bar" };
    window.history.pushState(stateObj, "ScanOC.com", new_url);
    //window.history.pushState(.object or string., .Title., ./new-url.);
    $("#jquery_jplayer_1").jPlayer("stop");
    force_page_rebuild = 1;
    first_load = 1;
    first_play = 1;
    buildpage();
    return false;
}

function clearpage() {
    if(buildpage_running == 1) {
       return false;
    }
    $('#main-data-table').html("");
}

var last_ajax;

function buildpage() {
    console.log("In build page running : " + buildpage_running);
    if(buildpage_running == 1) {
       return false;
    }
    buildpage_running = 1;
    update_api_url();
    if( ! api_url) {
        buildpage_running = 0;
        return false;
    }
    if(last_ajax) {
        // Cancel any pending ajax calls
        last_ajax.abort();
    }
    last_ajax = $.getJSON(api_url, function(data) {
      //console.log(data);
      //console.log("Checking for new calls")
      //console.log("Last Call " + last_call + " New last " + data.results[0].pk)
      if (data.results[0].pk != last_call || force_page_rebuild == 1) {
      console.log("Rebuild");
      force_page_rebuild = 0;
      var new_html = '<table class="table table-condensed"><thead> \
<tr><th>&nbsp;</th><th>TalkGroup</th><th>Description</th><th>Start Time</th></tr></thead><tbody>';
      new_id_list = []
      new_file_list = []
      new_tg_list = []
      for (var a in data.results) {
          new_id_list.unshift(data.results[a].pk);
          new_file_list.unshift(data.results[a].audio_file);
          new_tg_list.unshift(data.results[a].tg_name);
          button_type = "btn-default";
          if(currently_playing == data.results[a].pk) {
              console.log("Match on " + currently_playing)
              button_type = "btn-success"
          }
	  new_html += '<tr><td><button id="button_' + data.results[a].pk + '" type="button" class="btn play-btn ' + button_type + ' btn-sm" onclick="click_play_clip(\'//s3.amazonaws.com/scanoc-audio-001/' + data.results[a].audio_file + '\', ' + data.results[a].pk + ')"><span class="glyphicon glyphicon-play" aria-hidden="true"></span> Play </button></td> <td><!--<span class="glyphicon glyphicon-volume-off text-muted"></span>--><a onclick="return url_change(\'/tg/' + data.results[a].talkgroup_info.slug + '/\');" href="/tg/' + data.results[a].talkgroup_info.slug + '/"><span class="glyphicon glyphicon-filter btn-sm"></span></a><a href="/audio/' + data.results[a].slug + '/"><span class="glyphicon glyphicon-list-alt btn-sm"></span></a> ' + data.results[a].talkgroup_info.alpha_tag + '</td><td>' + data.results[a].talkgroup_info.description + '</td><td>' + data.results[a].local_start_datetime + '</td></tr>';
          new_html += '<tr class="unit_row"><td>' + data.results[a].print_play_length + '</td><td colspan="3">Units: ';
          for (unit in data.results[a].units) {
              if(data.results[a].units[unit].description) {
                  new_html += data.results[a].units[unit].description + ', ';
              } else {
                  if(js_logged_in_edit_units) {
                      new_html += '?<a href="/admin/radio/unit/' + data.results[a].units[unit].pk + '/change/">' + data.results[a].units[unit].dec_id + '</a>, ';
                  } else {
                      new_html += '?' + data.results[a].units[unit].dec_id + ', ';
                  }
              }
          }
          // Drop last ,
          new_html = new_html.slice(0, -2);
          new_html += '</td></tr>';
      }
      curr_id_list = new_id_list;
      curr_file_list = new_file_list;
      curr_tg_list = new_tg_list;
      new_html += '</table>';
      $('#main-data-table').html(new_html);
      }
      last_call = data.results[0].pk;
      first_load = 0;
    });
    buildpage_running = 0;
}

function click_play_clip(audio_file, audio_id){
    $("#button_start_scanner").hide();
    reset_play_list(audio_id);
    play_clip(audio_file, audio_id);
    play_next();
}

function play_clip(audio_file, audio_id){
      console.log("Play clip")     
      $(".play-btn").removeClass('btn-success').addClass('btn-default ');
      currently_playing=audio_id;
      if(audio_id == 0) {
        $("#button_start_scanner").removeClass('btn-default').addClass('btn-success ');
      } else {
	console.log("Trying to set button");
        $("#button_" + audio_id).removeClass('btn-default').addClass('btn-success ');
      }
      $("#jquery_jplayer_1").jPlayer("setMedia", {
         //oga: audio_file + ".ogg",
         //m4a: audio_file + ".m4a",
         mp3: audio_file + ".mp3",
       } );
       $("#jquery_jplayer_1").jPlayer("play");
}

function reset_play_list(audio_id){
    seen.length = 0; // Clear the array
    found_me = 0;
    for (var r_id in curr_id_list) {
        if(found_me == 0) {
            seen.push(curr_id_list[r_id]);
        }
        if(curr_id_list[r_id] == audio_id) {
            found_me = 1;
        }
    }
}

function play_next() {
    if(active_play == 0){
        return false;
    }
    for (var r_id in curr_id_list) {
        if ( seen.indexOf( curr_id_list[r_id] ) < 0 ) {
            if ( currently_playing == 0) {
              seen.push(curr_id_list[r_id]);
              //play_clip(audio_file, audio_id){
              mp3 = "//s3.amazonaws.com/scanoc-audio-001/" + curr_file_list[r_id];
              if(first_load == 0 && first_play == 0) { // Dont play them all on first load
                  tmp_title = '>>' + curr_tg_list[r_id] + '<< ' + page_title
                  document.title = tmp_title;
                  play_clip(mp3, curr_id_list[r_id]);
              }
            }
        }
    }
    if(first_load == 0) {
      first_play = 0;
    }
 }

function setup_player() {
      $("#jquery_jplayer_1").jPlayer({
       ready: function () {
        console.log("Setting up jPlayer")
       },
       ended: function() {
           active_play=1
           $("#button_" + currently_playing).removeClass('btn-success').addClass('btn-default ');
           $("#button_start_scanner").hide();
           currently_playing=0;
           $(document).prop('title', page_title);
       },
       swfPath: "https://jplayer.org/latest/dist/jplayer/",
       solution: "html,flash",
       supplied: "mp3",
       remainingDuration: true,
       errorAlerts: true,
       warningAlerts: true,
       volume: 1,
       cssSelectorAncestor: "",
       cssSelector: {
          title: "#title",
          play: "#jp1_play",
          pause: "#jp1_pause",
          stop: "#jp1_stop",
          mute: "#jp1_mute",
          unmute: "#jp1_unmute",
          currentTime: "#jp1_c_time",
         duration: "#jp1_duration"
       }
      });
      $("#jquery_jplayer_1").bind($.jPlayer.event.error + ".myProject", function(event) { 
          console.log("Error Event: type = " + event.jPlayer.error.type);
          active_play=1
          $("#button_" + currently_playing).removeClass('btn-success').addClass('btn-default ');
          currently_playing=0;
          $(document).prop('title', page_title);
      });
  }

$(document).ready(function(){ 
    if($(".tg-multi-select").length) {
        $(".tg-multi-select").select2()
    }
    setup_player();
    play_clip("//s3.amazonaws.com/scanoc-audio-001/point1sec", 0, 0)
    first_load = 1;
    buildpage();
    //setInterval(buildpage, 2000);
    play_next();
    setInterval(play_next, 500);

    //first_load = 0;
});

window.onfocus = function() {
    force_page_rebuild = 1;
    buildpage();
};
