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




  
    function showDiv(divId) {
      var divs = document.getElementsByClassName("tabby");
      for (var i = 0; i < divs.length; i++) {
          divs[i].style.display = "none";
      }
      document.getElementById(divId).style.display = "block";
  }
  function showGene2(number,dataN,genus) {
  
  var genusForIGV = genus.toString()
  var gene = document.getElementById("dropdownMenu"+number).parentNode.querySelector("[data-keyz]").getAttribute("data-keyz");
    var protein = document.getElementById("dropdownMenu"+number).innerText  
    changeData(dataN,gene,protein,genusForIGV)
    
  }
  
  function showGene(item,number) {
  
  document.getElementById("dropdownMenu"+number).innerHTML = item.innerHTML;
  
  
  }
  
  function changeData(data,gene,protein,genus){
  
  igv.removeAllBrowsers()
  
  
  var djangoData = $(data).data();
  
  
  
  var rvrValues = Object.values(djangoData);
  var splitvalues = []
  firstValue = rvrValues[0]
  if( data=='#rvr-data' || data=='#other-data' ){
  splitValues = firstValue.split("{'chrom':")
  }else{
  splitValues = firstValue.split("{")
  
  }
  
  var nucleotideArray = []
  var chromArray = []
  var resistancePosArray = []
  
  for(var i =1; i<splitValues.length;i++){
  
  var split2 =splitValues[i].split(",")
  
  if(split2.find(a =>a.includes(gene))){
  
  
  if(data == '#rvr-data'){
    
    chromArray.push(split2[0])
    
  resistancePosArray.push(split2[1].split(":")[1])
    var curr = split2[12].split(":")[1]
  curr = curr.replace(/['"]+/g, '').trim();
  
  nucleotideArray.push(curr)
  }else if(data == '#other-data'){
   
    chromArray.push(split2[0])
  resistancePosArray.push(split2[1].split(":")[1])
    var curr = split2[11].split(":")[1]
  curr = curr.replace(/['"]+/g, '').trim();
  
  nucleotideArray.push(curr)
  }else{
   
    var tempArray = split2[1].split(":")[1]
    
    
    var tempVar = tempArray.split("_")[1];
    if(genus == 'falciparum'){
      chromNumber = tempVar.slice(0,2)
      chromArray.push("Pf3D7_"+chromNumber+"_v3")
    }else if(genus == 'vivax'){
      chromNumber = tempVar.slice(0,2)
      chromArray.push("PvP01_"+chromNumber+"_v1")
    }else if(genus == 'malariae'){
      chromNumber = tempVar.slice(0,2)
      chromArray.push("PmUG01_"+chromNumber+"_v1")
    }else if(genus == 'ovale'){
      chromNumber = tempVar.slice(0,2)
      chromArray.push("PocGH01_"+chromNumber+"_v2")
    }else if(genus == 'knowlesi'){
      chromNumber = tempVar.slice(0,2)
      chromArray.push("ordered_PKNH_"+chromNumber+"_v2")
    }
  resistancePosArray.push(split2[0].split(":")[1])
    var curr = split2[3].split(":")[1]
  curr = curr.replace(/['"]+/g, '').trim();
  
  nucleotideArray.push(curr)
  }
  }
  }
  proteins = protein.trim();
  function getAllIndexes(arr, val) {
  var indexes = [], i = -1;
  while ((i = arr.indexOf(val, i+1)) != -1){
      indexes.push(i);
  }
  return indexes;
  }
  var currentChromosome = "";
  var currentPos = "";
  var currIndex = nucleotideArray.indexOf(proteins)
  if( data=='#rvr-data' || data=='#other-data' ){
  currentPos = resistancePosArray[currIndex]
  }else{
  var indexes = getAllIndexes(nucleotideArray, proteins);
  
  tempChr = []
  for (var i = 0; i < indexes.length; i++) {
  tempChr.push(resistancePosArray[indexes[i]])
  }
  firstPos = tempChr[0];
  lastPos = tempChr[tempChr.length-1];  
  
  }
  currentChromosome = chromArray[currIndex]
  currentChromosome = currentChromosome.replace(/[^\w\s!?]/g,'');
  currentChromosome = currentChromosome.replace(/\s+/g, '')
  
  var initiallocus = ""
  if( data=='#rvr-data' || data=='#other-data' ){
  initiallocus = currentChromosome+":"+currentPos
  
  }else{
  initiallocus = currentChromosome+":"+firstPos+"-"+lastPos
  
  }
  var locus = initiallocus.replace(/\s+/g, '')
  var url = ""
  
  url = '/static/fastafiles/'+ genus +'.fasta'
  index = '/static/fastafiles/'+ genus +'.fasta.fai'
  
  console.log(bam,bai,filename)
  var igvDiv = document.getElementById("igvDiv");
    var options =
      {
        reference:{
          id: genus,
          fastaURL: url,
          indexURL: index,
        },
        id: genus,
          locus: locus,
          
      };
      var options =
      {
        reference:{
          id: genus,
          fastaURL: url,
          indexURL: index,
          tracks: [
             {
                "name": filename[0],
                  "format": "bam",
                  "type": "alignment",
                   "url": bam,
                   "indexURL":bai,                     
                   "height": "300"
                   
             }
             
          
            ]}, id:genus,
          locus: locus}
      igv.createBrowser(igvDiv, options)
              .then(function (browser) {
              })
  }
  
              
  function showHidden(div){
    $(div).slideDown(1000);

    $("#mobile_dashboard").slideUp(1000);
  }
  function showMobile(div){
    $("#mobile_dashboard").slideDown(1000);
    $(div).slideUp(1000);
  
    
  }  
  var filename = [""]
  var bam = ""
  var bai = ""
  $(document).ready(function(){
    var djangoData = $("#species-data").data();
    
    getFileName(filename)
    var speciesValue = Object.values(djangoData);
    var firstValue = speciesValue[0]
    var splitValues = firstValue.split("{'species':")
    var splitagain = splitValues[1].split(",");
    var genus = splitagain[0].replace(/[^\w\s!?]/g,'');
    genus = genus.replace(/\s+/g, '')
    var  url = '/static/fastafiles/'+ genus +'.fasta'
  var index = '/static/fastafiles/'+ genus +'.fasta.fai'
  bam = '/static/results/'+filename+".bam"
  bai = '/static/results/' +filename+ ".bam.bai"
  console.log(bam)
    var igvDiv = document.getElementById("igvDiv");
    var options =
      {
        reference:{
          id: genus,
          fastaURL: url,
          indexURL: index,
          tracks: [
             {
                "name": filename,
                  "format": "bam",
                  "type": "alignment",
                   "url": bam,
                   "indexURL":bai,                     
                   "height": "300"
                   
             }
             
          
            ]}}
    igv.createBrowser(igvDiv,options)
  })

  function getFileName(filenameRef){
    var resultID = $("#result-id").data();
    var resultsValue = Object.values(resultID)
    var resultsFirst = resultsValue[0]
    var resultsSplit = resultsFirst.split("[{'id':")
    var resultsSplitAgain = resultsSplit[1].split(",");
    filenameRef[0] = resultsSplitAgain[0].replace(/[ \']/g,'');
    filenameRef[0] = filenameRef[0]//.replace(/\s+/g, '')
    console.log(filenameRef[0])
}