am5.ready(function() {


  var root = am5.Root.new("chartdiv");
  
  
  root.setThemes([
    am5themes_Animated.new(root)
  ]);
  
  
  var chart = root.container.children.push(am5map.MapChart.new(root, {
    panX: "rotateX",
    panY: "rotateY",
    projection: am5map.geoOrthographic(),
    paddingBottom: 20,
    paddingTop: 20,
    paddingLeft: 20,
    paddingRight: 20
  }));
  
  var cont = chart.children.push(
    am5.Container.new(root, {
      layout: root.horizontalLayout,
      x: 20,
      y: 40
    })
  );
  
  
  var backgroundSeries = chart.series.push(am5map.MapPolygonSeries.new(root, {}));
  
  backgroundSeries.mapPolygons.template.setAll({
    fill: am5.color("#2B65EC"),
    fillOpacity: 0.5,
    strokeOpacity: 0
  });
  backgroundSeries.data.push({
    geometry:
      am5map.getGeoRectangle(90, 180, -90, -180)
  });
  // Create main polygon series for countries
  
  var polygonSeries = chart.series.push(
    am5map.MapPolygonSeries.new(root, {
      geoJSON: am5geodata_worldLow,
     
    })
  );
  
  polygonSeries.mapPolygons.template.setAll({
    fill: am5.color("#eee"),
    
    strokeWidth: 0.5,
    stroke: root.interfaceColors.get("background")
  });
  
  
  
  var pointSeries = chart.series.push(am5map.MapPointSeries.new(root, {}));
  var colorset = am5.ColorSet.new(root, {});
  
  pointSeries.bullets.push(function () {
    var container = am5.Container.new(root, {});
  
    var circle = container.children.push(
      am5.Circle.new(root, {
        radius: 8,
        tooltipY: 0,
        fill: am5.color(0xff0000),
        strokeOpacity: 0,
        tooltipText: "{title}"
      })
    );
  
    var circle2 = container.children.push(
      am5.Circle.new(root, {
        radius:14,
        tooltipY: 0,
        fill: am5.color(0xff0000),
        strokeOpacity: 0,
        tooltipText: "{title}"
      })
    );
  
    circle.animate({
      key: "scale",
      from: 1,
      to: 4,
      duration: 600,
      easing: am5.ease.out(am5.ease.cubic),
      loops: Infinity
    });
    circle.animate({
      key: "opacity",
      from: 1,
      to: 0,
      duration: 3000,
      easing: am5.ease.out(am5.ease.cubic),
      loops: Infinity
    });
  
    return am5.Bullet.new(root, {
      sprite: container
    });
  });
  
  var regions = [
    
    
  ];
  
  // Rotate animation
  chart.animate({
    key: "rotationX",
    from: 0,
    to: 360,
    duration: 6000,
    loops: Infinity
  });
  $(document).ready(function(){
   
   
    var region = $('#region').data();
  var regionalValues = Object.values(region);
  
  firstValue = regionalValues[0]
  var splitValues = firstValue.split(":")
  beforeTrim = splitValues[1];
  finalRegion = beforeTrim.replace(/[^\w\s!?]/g,'');
  
  if(finalRegion == " Western Africa" ){
  regions.push({
      title: "West Africa",
      latitude: 13,
      longitude: 2
    },)
    
    
    addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
    
  }else if (finalRegion == " Oceania"){
  
    regions.push({
      title: "Oceania",
      latitude:-15,
      longitude: 140
    },)
    addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
    
  }else if (finalRegion == " Eastern Africa"){
    regions.push({
      title: "East Africa",
      latitude: 14,
      longitude: 33
    },)
    addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
    
  }else if (finalRegion == " Africa"){
    regions.push({
      title: "Africa",
      latitude: 6.6,
      longitude: 21
    },)
    addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
    
  }else if (finalRegion == " Southeast Asia"){
    regions.push({
      title: "Southeast Asia",
      latitude: 7,
      longitude: 111
    },)
    addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
    
  }else if (finalRegion == " Horn of Africa"){
    regions.push({
      title: "Horn of Africa",
      latitude: 7,
      longitude: 43
    },)
    addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
    
  }else if (finalRegion == " South America"){
    regions.push({
      title: "South America",
      latitude: -10,
      longitude: -60
    },)
    addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
    
  }
  })
  
  
  function addregion(longitude, latitude, title) {
    pointSeries.data.push({
      geometry: { type: "Point", coordinates: [longitude, latitude] },
      title: title
    });
  }
  
  
  chart.appear(1000, 100);
  
  
  }); 