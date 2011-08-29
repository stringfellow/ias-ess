function initialize_map (data) {
    // data
    // [ { features:{...}, { name:...}, { style:...} }, {...} ]

    var latlng = new google.maps.LatLng(54, -1);
    var myOptions = {
      zoom: 5,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"),
        myOptions);

    var marker_obj = {};   // all 3 are
    var cluster_obj = {};  // referenced by
    var style_obj = {};    // the same name (data[i].name)

    for (var i = 0; i < data.length; i++) {
        var g_clusters = [];
        for (var id in data[i].features) {
            var lat = data[i].features[id][0];
            var lng = data[i].features[id][1];
            var g_coord = new google.maps.LatLng(lat, lng);
            var g_marker = new google.maps.Marker({'position': g_coord});
            g_marker.set('id', id);
            g_clusters.push(g_marker);
        }
        marker_obj[data[i].name] = g_clusters;
        style_obj[data[i].name] = data[i].style || defaultStyle;
        var marker_cluster = new MarkerClusterer(map, g_clusters,
            {styles: data[i].style || defaultStyle});
        marker_cluster.set('name', data[i].name);
        handle_cluster_display(data[i].name);
        cluster_obj[data[i].name] = marker_cluster;
    }


    function handle_cluster_display (cluster_name) {
        // it is not clear from the api how to toggle cluster visibility
        // so my workaround is to clear and recreate the clusters each time
        var test = true;
        $('#' + cluster_name).click(function() {
            if (test === true) {
                cluster_obj[cluster_name].clearMarkers();
                test = false;
            } else {
                var marker_cluster = new MarkerClusterer(map, 
                    marker_obj[cluster_name], {styles: style_obj[cluster_name]});
                marker_cluster.set('name', cluster_name);
                // updating the cluster_obj with the new MarkerClusterer
                cluster_obj[cluster_name] = marker_cluster;
                test = true;
            }
        });
    }


    //Class hook for changing colour
    $(function() {
       $('.checkbox-row input:checked').click(function() {
          $(this).closest('.checkbox-row').toggleClass('checkbox-row-unchecked');
       });
    });

};





