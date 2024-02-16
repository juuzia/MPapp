
document.addEventListener('DOMContentLoaded', function() {
  
  
  am5.ready(function() {
    initialiseChart("chartdiv-mobile");
    initialiseChart("chartdiv-desktop");
        

    }); 
});
function resizeChart(chart) {
  if (chart) {
      chart.invalidateSize();
  }
}

// Example usage


function initialiseChart(targetDivId){
  const regionMetas = document.querySelectorAll('meta[id^="region-"]');
  var root = am5.Root.new(targetDivId);
    
    
    root.setThemes([
      am5themes_Animated.new(root)
    ]);
    
    if (targetDivId ==="chartdiv-mobile"){
      var chart = root.container.children.push(am5map.MapChart.new(root, {
        panX: "none",
        panY: "none",
        wheelX: "none",
        wheelY: "none",
        pinchZoom: false,
        projection: am5map.geoNaturalEarth1(),
    
      }));
     
    }else{
      var chart = root.container.children.push(am5map.MapChart.new(root, {
     
        projection: am5map.geoNaturalEarth1(),
        paddingBottom: 20,
        paddingTop: 20,
        paddingLeft: 20,
        paddingRight: 20,
        minZoomLevel:1.5,
        homeZoomLevel: 1.5,
        maxZoomLevel: 1.5,
        homeGeoPoint: { longitude: 30, latitude:-20 }
    
      }));
    }
   
    // var cont = chart.children.push(
    //   am5.Container.new(root, {
    //     layout: root.horizontalLayout,
    //     x: 20,
    //     y: 40
    //   })
    // );
    
    // let heatLegend = chart.children.push(am5.HeatLegend.new(root, {
    //   orientation: "horizontal",
    //   startColor: am5.color(0xff621f),
    //   endColor: am5.color(0x661f00),
    //   startText: "Lowest",
    //   endText: "Highest",
    //   stepCount: 1,
    //   startValue: 0,
    //   endValue: 1,
    //   y:100
      
    // }));

    // heatLegend.startLabel.setAll({
    //   fontSize: 7,
    //   fill: heatLegend.get("startColor")
    // });
    // heatLegend.endLabel.setAll({
    //   fontSize: 7,
    //   fill: heatLegend.get("startColor")
    // });
        
    var backgroundSeries = chart.series.push(am5map.MapPolygonSeries.new(root, {}));
    
    backgroundSeries.mapPolygons.template.setAll({
      fill: am5.color("#ff5900"),
      fillOpacity: 0.5,
      strokeOpacity: 0
    });
    
    
    let polygonSeries = chart.series.push(am5map.MapPolygonSeries.new(root, {
      geoJSON: am5geodata_worldLow,
      exclude: ["AQ"],
      calculateAggregates: true,
      valueField : "value"
      // ,"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","UK","IT","LT","LV","LU","MT","NL","PL","PT","RO","SK","SI","ES",
      // "SE","GB","NO","CH","LI","IS","AL","BA","MD","GL","US","CA","MX","RU","SJ","UA","BY","CN","TM","TR","TC","KZ","RS","XK","ME","MK","GE","AZ","AM","IR",
      // "IQ","IL","JO","SA","YE","OM","AE","KW","MN","SY","PS","LB","QA","TJ","UZ","TW","KG","JP","KR","KP","PG","AU","NZ","NI","CR","GT","PA","DO","HN","SV",
      // "CU","HT","PR","BZ","JM","BS"
    }));
    
    polygonSeries.mapPolygons.template.setAll({
      fill: am5.color("#ff5900"),
      tooltipText: "{name}: {value}%",
      strokeWidth: 0.5,
      stroke: root.interfaceColors.get("background"),
      
    });
    
    polygonSeries.set("heatRules", [{
      target: polygonSeries.mapPolygons.template,
      dataField: "value",
      min: am5.color("#ff5900"),
      max: am5.color("#6e2501"),
      key: "fill"
    }]);
    // polygonSeries.mapPolygons.template.events.on("pointerover", function(ev) {
    //   heatLegend.showValue(ev.target.dataItem.get("value"));
    // });
    // var pointSeries = chart.series.push(am5map.MapPointSeries.new(root, {}));
    // var colorset = am5.ColorSet.new(root, {});
    
    // pointSeries.bullets.push(function () {
    //   var container = am5.Container.new(root, {});
    
    //   var circle = container.children.push(
    //     am5.Circle.new(root, {
    //       radius: 8,
    //       tooltipY: 0,
    //       fill: am5.color(0xff0000),
    //       strokeOpacity: 0,
    //       tooltipText: "{title}"
    //     })
    //   );
    
    //   var circle2 = container.children.push(
    //     am5.Circle.new(root, {
    //       radius:14,
    //       tooltipY: 0,
    //       fill: am5.color(0xff0000),
    //       strokeOpacity: 0,
    //       tooltipText: "{title}"
    //     })
    //   );
    
    //   circle.animate({
    //     key: "scale",
    //     from: 1,
    //     to: 4,
    //     duration: 600,
    //     easing: am5.ease.out(am5.ease.cubic),
    //     loops: Infinity
    //   });
    //   circle.animate({
    //     key: "opacity",
    //     from: 1,
    //     to: 0,
    //     duration: 3000,
    //     easing: am5.ease.out(am5.ease.cubic),
    //     loops: Infinity
    //   });
    
    //   return am5.Bullet.new(root, {
    //     sprite: container
    //   });
    // });
    
    

    $(document).ready(function(){
      regions_probs = []
      

  regionMetas.forEach(meta => {
    const region = meta.getAttribute('data-region');
    let value = meta.getAttribute('data-probability');
    value = value*100
    if (region ==="Central Africa"){
      regions_probs.push({"id":"CF",
      "value":value})
      regions_probs.push({"id":"TD",
      "value":value})
      regions_probs.push({"id":"CM",
      "value":value})
      regions_probs.push({"id":"AO",
      "value":value})
      regions_probs.push({"id":"GQ",
      "value":value})
      regions_probs.push({"id":"GA",
      "value":value})
      regions_probs.push({"id":"CD",
      "value":value})
      regions_probs.push({"id":"ST",
      "value":value})
      regions_probs.push({"id":"CG",
      "value":value})
      regions_probs.push({"id":"BI",
      "value":value})
      regions_probs.push({"id":"RW",
      "value":value})
      regions_probs.push({"id":"SS",
      "value":value})  
      regions_probs.push({"id":"SD",
      "value":value})
        
    }else if (region ==="Eastern Africa"){
      
      regions_probs.push({"id":"KE",
      "value":value})
      regions_probs.push({"id":"TZ",
      "value":value})
      regions_probs.push({"id":"ET",
      "value":value})
      regions_probs.push({"id":"SO",
      "value":value})
      regions_probs.push({"id":"DJ",
      "value":value})
      regions_probs.push({"id":"KM",
      "value":value})
      regions_probs.push({"id":"MG",
      "value":value})
      regions_probs.push({"id":"MW",
      "value":value})
      regions_probs.push({"id":"MU",
      "value":value})
      regions_probs.push({"id":"MZ",
      "value":value})
      regions_probs.push({"id":"SC",
      "value":value})
      regions_probs.push({"id":"ER",
      "value":value})
      regions_probs.push({"id":"RE",
      "value":value})
      regions_probs.push({"id":"ZW",
      "value":value})
      regions_probs.push({"id":"ZA",
      "value":value})
      regions_probs.push({"id":"UG",
      "value":value})
      
    }else if (region ==="South America"){
      regions_probs.push({"id":"AR",
      "value":value})
      regions_probs.push({"id":"BO",
      "value":value})
      regions_probs.push({"id":"BR",
      "value":value})
      regions_probs.push({"id":"CL",
      "value":value})
      regions_probs.push({"id":"EC",
      "value":value})
      regions_probs.push({"id":"FK",
      "value":value})
      regions_probs.push({"id":"GF",
      "value":value})
      regions_probs.push({"id":"GY",
      "value":value})
      regions_probs.push({"id":"PY",
      "value":value})
      regions_probs.push({"id":"PE",
      "value":value})
      regions_probs.push({"id":"GS",
      "value":value})
      regions_probs.push({"id":"SR",
      "value":value})
      regions_probs.push({"id":"UY",
      "value":value})
      regions_probs.push({"id":"VE",
      "value":value})

    }else if (region ==="South Asia"){
      regions_probs.push({"id":"AF",
      "value":value})
      regions_probs.push({"id":"BD",
      "value":value})
      regions_probs.push({"id":"BT",
      "value":value})
      regions_probs.push({"id":"IN",
      "value":value})
      regions_probs.push({"id":"NP",
      "value":value})
      regions_probs.push({"id":"MV",
      "value":value})
      regions_probs.push({"id":"PK",
      "value":value})
      regions_probs.push({"id":"LK",
      "value":value})

    }else if (region ==="Southeast Asia"){
      regions_probs.push({"id":"BN",
      "value":value})
      regions_probs.push({"id":"KH",
      "value":value})
      regions_probs.push({"id":"ID",
      "value":value})
      regions_probs.push({"id":"LA",
      "value":value})
      regions_probs.push({"id":"MY",
      "value":value})
      regions_probs.push({"id":"MM",
      "value":value})
      regions_probs.push({"id":"PH",
      "value":value})
      regions_probs.push({"id":"SG",
      "value":value})
      regions_probs.push({"id":"TH",
      "value":value})
      regions_probs.push({"id":"VN",
      "value":value})
      regions_probs.push({"id":"TL",
      "value":value})
    }else if (region==="Western Africa"){
      regions_probs.push({"id":"BJ",
      "value":value})
      regions_probs.push({"id":"NE",
      "value":value})
      regions_probs.push({"id":"NG",
      "value":value})
      regions_probs.push({"id":"SH",
      "value":value})
      regions_probs.push({"id":"SN",
      "value":value})
      regions_probs.push({"id":"SL",
      "value":value})
      regions_probs.push({"id":"TG",
      "value":value})
      regions_probs.push({"id":"CI",
      "value":value})
      regions_probs.push({"id":"LR",
      "value":value})
      regions_probs.push({"id":"GM",
      "value":value})
      regions_probs.push({"id":"CV",
      "value":value})
      regions_probs.push({"id":"ML",
      "value":value})
      regions_probs.push({"id":"BF",
      "value":value})
      regions_probs.push({"id":"GN",
      "value":value})
      regions_probs.push({"id":"GW",
      "value":value})
    }
    
    });
      
      
    // var regionalValues = Object.values(region);
    // firstValue = regionalValues[0]
    // var splitValues = firstValue.split(":")
    // beforeTrim = splitValues[1];
    // finalRegion = beforeTrim.replace(/[^\w\s!?]/g,'');
    
    // if(finalRegion == " Western Africa" ){
    // regions.push({
    //     title: "West Africa",
    //     latitude: 13,
    //     longitude: 2
    //   },)
      
      
    //   addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
      
    // }else if (finalRegion == " Oceania"){
    
    //   regions.push({
    //     title: "Oceania",
    //     latitude:-15,
    //     longitude: 140
    //   },)
    //   addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
      
    // }else if (finalRegion == " Eastern Africa"){
    //   regions.push({
    //     title: "East Africa",
    //     latitude: 14,
    //     longitude: 33
    //   },)
    //   addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
      
    // }else if (finalRegion == " Africa"){
    //   regions.push({
    //     title: "Africa",
    //     latitude: 6.6,
    //     longitude: 21
    //   },)
    //   addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
      
    // }else if (finalRegion == " Southeast Asia"){
    //   regions.push({
    //     title: "Southeast Asia",
    //     latitude: 7,
    //     longitude: 111
    //   },)
    //   addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
      
    // }else if (finalRegion == " Horn of Africa"){
    //   regions.push({
    //     title: "Horn of Africa",
    //     latitude: 7,
    //     longitude: 43
    //   },)
    //   addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
      
    // }else if (finalRegion == " South America"){
    //   regions.push({
    //     title: "South America",
    //     latitude: -10,
    //     longitude: -60
    //   },)
    //   addregion(regions[0].longitude, regions[0].latitude, regions[0].title);
      
    // }
    polygonSeries.data.setAll(regions_probs)
   
     })
    
    
    // function addregion(longitude, latitude, title) {
    //   pointSeries.data.push({
    //     geometry: { type: "Point", coordinates: [longitude, latitude] },
    //     title: title
    //   });
    // }
    
    setTimeout(() => {
      polygonSeries.data.values.forEach((dataItem, index) => {
      
        if (!dataItem.value) {
          dataItem.value = 0
        }
      });
      chart.appear(1000, 100);
      if(targetDivId==="chartdiv-desktop"){
      chart.goHome()

      }
    }, 1000);
    
    
    
}


  
    function showDiv(divId) {
      var divs = document.getElementsByClassName("tabby");
      for (var i = 0; i < divs.length; i++) {
          divs[i].style.display = "none";
      }
      document.getElementById(divId).style.display = "block";
  }
  function showGene2(number,dataN,genus) {
    
    
    var genusForIGV = genus.toString()
 
    number = number.trimStart()
    gene = number.split(" ")[0]
    protein = number.split(" ")[1]
    console.log(number)
    console.log(protein)
    console.log(gene)
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
  if( data!="#miss-data" ){
  splitValues = firstValue.split("{'chrom':")
  
  }else{
  splitValues = firstValue.split("{")
  
  }
  
  var proteinArray = []
  var nucleotideArray = []
  var chromArray = []
  var resistancePosArray = []
  
  for(var i =1; i<splitValues.length;i++){
  
  var split2 =splitValues[i].split(",")
  if(split2.find(a =>a.includes(gene))){
  
  
  if(data != '#miss-data'){
    chromArray.push(split2[0])
    
  resistancePosArray.push(split2[1].split(":")[1])
    
  var curr = split2[17].split(":")[1]
   
  curr = curr.replace(/['"]+/g, '').trim();
  var curr2 = split2[16].split(":")[1]
  curr2 = curr2.replace(/['"]+/g, '').trim();
  nucleotideArray.push(curr2)
  proteinArray.push(curr)
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
  var currIndex ="";
  console.log(proteins)
  if(nucleotideArray.includes(proteins)){
    currIndex = nucleotideArray.indexOf(proteins)
  }else{
    console.log("ho")

    currIndex = proteinArray.indexOf(proteins)
  }
  
  
  if( data!="miss-data" ){
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
  console.log(chromArray)
  currentChromosome = chromArray[currIndex]
  console.log(currentChromosome)
  console.log(currIndex)
  currentChromosome = currentChromosome.replace(/[^\w\s!?]/g,'');
  currentChromosome = currentChromosome.replace(/\s+/g, '')
  var initiallocus = ""
  if( data!="miss-data" ){
  initiallocus = currentChromosome+":"+currentPos
  
  }else{
  initiallocus = currentChromosome+":"+firstPos+"-"+lastPos
  
  }
  var locus = initiallocus.replace(/\s+/g, '')
  var url = ""
  
  url = '/static/fastafiles/'+ genus +'.fasta'
  index = '/static/fastafiles/'+ genus +'.fasta.fai'
  
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
}

