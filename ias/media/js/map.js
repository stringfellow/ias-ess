function initialize_map (data) {
    // data
    // [ { features:{...}, { name:...}, { style:...} }, {...} ]

    var latlng = new google.maps.LatLng(54, -1);
    var myOptions = {
      zoom: 5,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var hiddenMap = new google.maps.Map(
        document.getElementById("map_hidden_canvas"), myOptions);
    var map = new google.maps.Map(document.getElementById("map_canvas"),
        myOptions);

    // monkeypatch as per http://stackoverflow.com/questions/4060241/how-to-show-hide-a-markercluster-in-google-maps-v3
    MarkerClusterer.prototype.remove = function () {};

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
        
        var marker_cluster = new MarkerClusterer(map, g_clusters,
            {styles: data[i].style || defaultStyle});
        marker_cluster.set('name', data[i].name);
        handle_cluster_display(marker_cluster);
    }
    
    function handle_cluster_display(marker_cluster) {
        $('#' + marker_cluster.name).click(function() {
            if (marker_cluster.getMap() === hiddenMap) {
                marker_cluster.set('map', map);
            } else {
                marker_cluster.set('map', hiddenMap);
            }
            marker_cluster.resetViewport();
            marker_cluster.redraw();
        });
    }

    //Class hook for changing colour
    $(function() {
       $('.checkbox-row input:checked').click(function() {
          $(this).closest('.checkbox-row').toggleClass('checkbox-row-unchecked');
       });
    });

};





