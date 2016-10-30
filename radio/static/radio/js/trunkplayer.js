active_play=1;
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
curr_tg_slug_list = [];
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
var pagination_older_url = null;
var pagination_newer_url = null;
var muted_tg = {}

var buildpage_running = 0;

function update_scan_list() {
    start_socket();   
    buildpage();
}

function mute_click(tg) {
    console.log("User click on Mute for TG " + tg)
    if (muted_tg[tg]) {
        muted_tg[tg] = false;
        $('.mute-tg-' + tg).removeClass('mute-mute ');
    } else {
        muted_tg[tg] = true;
        $('.mute-tg-' + tg).addClass('mute-mute ');
    }
}

function update_pagination_links() {
    pagination_html = "";
    if(pagination_newer_url) {
        pg_array = pagination_newer_url.split( '?' );
        new_url = window.location.pathname + '?' + pg_array[1];
        home_url = window.location.pathname;
        pagination_html = '<button onclick="url_change(\'' + home_url + '\')">Current</button>'
        pagination_html += '<button onclick="url_change(\'' + new_url + '\')">Newer</button>'
    }
    if(pagination_older_url) {
        pg_array = pagination_older_url.split( '?' );
        new_url = window.location.pathname + '?' + pg_array[1];
        pagination_html += '<button onclick="url_change(\'' + new_url + '\')">Older</button>'
    }
    $('#pagination').html(pagination_html);
}
function update_api_url() {
    url_params = document.location.search
    pathArray = window.location.pathname.split( '/' );
    pathArray.shift();
    console.log("url build");
    if(pathArray[0] == "scan2") {
      pathArray[0] = "scan";
    }
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
        console.log("URL End " + url_params)
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
    $('#main-data-table').html("<p style='text-align: center'><img src='/static/radio/img/loader.gif' />");
    $('#pagination').html("");
}

function update_menu() {
    // ScanList Header
    url = '/api_v1/menuscanlist/';
    new_html_live = '';
    new_html = '';
    $.getJSON(url, function(data) {
        for (var a in data.results) {
            new_html_live += '<li><a href="/scan/' + data.results[a].scan_name + '/" onclick="return url_change(\'/scan/' + data.results[a].scan_name + '/\');">' + data.results[a].scan_description + '</a></li>';
            new_html += '<li><a href="/scan/' + data.results[a].scan_name + '/">' + data.results[a].scan_description + '</a></li>';
        }
        a  = '<li class="divider"></li>';
        a += '<li><a href="/userscan/">Custom Scan List</a></li>';
        new_html_live += a
        new_html += a
        $('#menu-scanlist-live').html(new_html_live);
        $('#menu-scanlist').html(new_html);
    });

    // TalkGroup Header
    url2 = '/api_v1/menutalkgrouplist/';
    new_html2_live = '';
    new_html2 = '';
    $.getJSON(url2, function(data) {
        for (var a in data.results) {
            new_html2_live += '<li><a href="/tg/' + data.results[a].tg_slug + '/" onclick="return url_change(\'/tg/' + data.results[a].tg_slug + '/\');">' + data.results[a].tg_name + '</a></li>';
            new_html2 += '<li><a href="/tg/' + data.results[a].tg_slug + '/">' + data.results[a].tg_name + '</a></li>';
        }
        a  = '<li class="divider"></li>';
        a += '<li><a href="/talkgroups/">List All Talkgroups</a></li>';
        new_html2_live += a
        new_html2 += a
        $('#menu-talkgrouplist-live').html(new_html2_live);
        $('#menu-talkgrouplist').html(new_html2);
    });


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
      console.log(data);
      //console.log("Checking for new calls")
      //console.log("Last Call " + last_call + " New last " + data.results[0].pk)
      if (data.results[0].pk != last_call || force_page_rebuild == 1) {
      console.log("Rebuild");
      force_page_rebuild = 0;
      var new_html = '';
      new_id_list = [];
      new_file_list = [];
      new_tg_list = [];
      new_tg_slug_list = [];
      js_logged_in_edit_units = 0; // XXX Get from JS config
      count=0;
      for (var a in data.results) {
          curr_results = data.results[a];
          curr_id = curr_results.pk;

          new_id_list.unshift(data.results[a].pk);
          new_file_list.unshift(data.results[a].audio_file);
          new_tg_list.unshift(data.results[a].tg_name);
          new_tg_slug_list.unshift(data.results[a].talkgroup_info.slug);
          button_type = "btn-default";
          if(currently_playing == data.results[a].pk) {
              console.log("Match on " + currently_playing)
              button_type = "active-trans"
          }
          tg_muted="";
          if (muted_tg[data.results[a].talkgroup_info.slug]) {
            tg_muted="mute-mute ";
          }

          new_html += '<div id="row-' + curr_id + '" class="row">'
          new_html += '<div class="top-data"><span class="player-action glyphicon glyphicon-play" aria-hidden="true" onclick="return click_play_clip(\'//s3.amazonaws.com/scanoc-audio-001/' + curr_results.audio_file + '\', ' + curr_id + ');"></span><span class="talk-group talk-group-' + curr_results.talkgroup_info.slug + '">' + data.results[a].talkgroup_info.alpha_tag + '</span> <span class="talk-group-descr">' + curr_results.talkgroup_info.description + ' </span><span class="tran-length">' + curr_results.print_play_length + '</span><span class="tran-start-time">' + curr_results.local_start_datetime + '</span></div>';
          new_html += '<div class="unit-data"><span class="unit-id-1 unit-list">';
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
          new_html  = new_html.slice(0, -2);
          new_html += '</span>';
          new_html += '<span class="tran-menu">';
          new_html += '<div class="btn-group">';
          new_html += '<a class="btn dropdown-toggle tran-menu-a" data-toggle="dropdown" href="#">';
          new_html += '<i class="fa fa-list-ul" aria-hidden="true" title="Menu"></i>';
          new_html += '</a>';
          new_html += '<ul class="dropdown-menu pull-right">';
          new_html += '<li><a href="#"><i class="fa fa-filter fa-fw"></i> Hold on TalkGroup</a></li>';
          new_html += '<li><a href="#"><i class="fa fa-volume-off fa-fw"></i> Mute TalkGroup</a></li>';
          new_html += '<li><a href="#"><i class="fa fa-pencil fa-fw"></i> Edit Unit ID</a></li>';
          new_html += '<li><a href="#"><i class="fa fa-info-circle fa-fw"></i> Details</a></li>';
          new_html += '<li class="divider"></li>';
          new_html += '<li><a href="#"><i class="fa fa-trash-o fa-fw"></i> Flag for delete</a></li>';
          new_html += '</ul>';
          new_html += '</div>';
          new_html += '</span>';
          new_html += '</div>';
          new_html += '</div>';
      }
      curr_id_list = new_id_list;
      curr_file_list = new_file_list;
      curr_tg_list = new_tg_list;
      curr_tg_slug_list = new_tg_slug_list;
      $('#main-data-table').html(new_html);
      pagination_older_url = data.next;
      pagination_newer_url = data.previous;
      update_pagination_links();
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
      $(".play-btn").removeClass('active-trans');
      currently_playing=audio_id;
      if(audio_id == 0) {
        $("#button_start_scanner").removeClass('btn-default').addClass('btn-success ');
      } else {
	console.log("Trying to set button");
        $("#button_" + audio_id).removeClass('btn-default').addClass('btn-success ');
        $("#row-" + audio_id).addClass('active-trans ');
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
              // See if we are muted
              if(muted_tg[curr_tg_slug_list[r_id]]) {
                 return;
              }
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
           $("#row_" + currently_playing).removeClass('active-trans');
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
          $("#button_" + currently_playing).removeClass('active-trans');
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
    update_menu();

    //first_load = 0;
});

window.onfocus = function() {
    force_page_rebuild = 1;
    buildpage();
};
