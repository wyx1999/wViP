function plot_word_cloud_type2() {
   wordcloud_chart.showLoading();
   var width = $("#width_type2").val();
   var height = $("#height_type2").val();
   var max_font_size = $("#max_font_size_type2").val();
   var min_font_size = $("#min_font_size_type2").val();
   var show_img = $("#show_img").attr('alt');
   var font_type = $("#font_type").val();
   var color_start = $("#color_start").val();
   var color_end = $("#color_end").val();
   var frequency=new Array();
   var obj=document.getElementById("second_tbody");
   var rows=obj.rows;
   var len = rows.length;
  if (len>500){len=500};

   for(var i=0;i<len;i++){ //行
       var e_p =  {name: rows[i].cells[0].innerHTML, value: rows[i].cells[1].childNodes[0].value,}
       frequency[i]=e_p;
   }
   var colorArr = new Array();
   colorArr = colorGradient(color_start, color_end, 50); // 颜色渐变色数组
 //  frequency.sort(function(a,b){return b.value-a.value});
   for(var i=0;i<len;i++){
        if (i<50){
            frequency[i]['textStyle']={
                color: colorArr[i]
            }
        }
        else{
            frequency[i]['textStyle']={
                color: colorArr[49]
            }
        }

   }

   var maskImage = new Image();
   maskImage.src = document.getElementById("show_img").src;
    if (len==0){
        for(var i=0;i<200;i++){ //行
            x = i%50;
           var e_p =  {name: 'None', value: 100-x}
           frequency[i]=e_p;
           frequency[i]['textStyle']={
                    color: colorArr[x]
           }
       }
   };

 //   chartDom.removeAttribute('_echarts_instance_');
    var wordcloud_option = {
            toolbox: {
                show: false,
            },
            tooltip: {},
            series: [{
                type: 'wordCloud',
                gridSize: 1,

                sizeRange: [min_font_size, max_font_size],
                rotationRange: [-90, 90],
                width: width,
                height: height,
                drawOutOfBound: false,
                maskImage: maskImage,
                textStyle: {
                    fontFamily: font_type,
                },

                data: frequency,
            }]
        };
        setTimeout(function () {
            wordcloud_chart.setOption(wordcloud_option,true);
            wordcloud_chart.resize;
            wordcloud_chart.setOption({
                    series: [{
                    type: 'wordCloud',
                    gridSize: 2,
                }]
            });
        }, 500);
        setTimeout(function () {

            wordcloud_chart.setOption({
                    series: [{
                    type: 'wordCloud',
                    gridSize: 2,
                }]
            });
        }, 2000);
        setTimeout(function () {

            wordcloud_chart.hideLoading();
        }, 5000);

}

function plot_word_cloud() {
   $(".loading").fadeIn();
   $(".type1").show();
    $(".type2").hide();
    $("#wordcloudModalLabel").text('Static Visualization');
   var text = $("#text").val();
   var is_stopwords = $("#is_stopwords").is(':checked');
   var is_dictionary = $("#is_dictionary").is(':checked');
   var is_nlp = 'true';
   var is_mask = $("#is_mask").is(':checked');

   var width = $("#width").val();
   var height = $("#height").val();
   var scale = $("#scale").val();
   var prefer_horizontal = $("#prefer_horizontal").val();
   var max_font_size = $("#max_font_size").val();
   var min_font_size = $("#min_font_size").val();
   var show_img = $("#show_img").attr('alt');
   var font_type = $("#font_type").val();
   var colormaps = $("#colormaps").val();
   var ColorByMask = $("#ColorByMask").is(":checked");
   var ColorBySize = $("#ColorBySize").is(":checked"); //ture
   var ColorBySize_threshold = $("#ColorBySize_threshold").val();
   var stamp = $("#stamp").text();

   var frequency={};
   var obj=document.getElementById("second_tbody");
   var rows=obj.rows;


   for(var i=0;i<rows.length;i++){ //行
       frequency[rows[i].cells[0].innerHTML]=rows[i].cells[1].childNodes[0].value;
   }

   $.post("/client/plot_wordcloud/",
    {
        text:text,
        is_stopwords:is_stopwords,
        is_dictionary:is_dictionary,
        is_nlp:is_nlp,
        is_mask:is_mask,
        width:width,
        height:height,
        scale:scale,
        prefer_horizontal:prefer_horizontal,
        max_font_size:max_font_size,
        min_font_size:min_font_size,
        show_img:show_img,
        font_type:font_type,
        colormaps:colormaps,
        ColorByMask:ColorByMask,
        ColorBySize:ColorBySize,
        ColorBySize_threshold:ColorBySize_threshold,
        stamp: stamp,
        frequency:JSON.stringify(frequency),
    },
    function(data){
        // var url = "data:image/png;base64,";
        //  document.getElementById("wordcloud_pic").src = url+ data.wordcloud_pic;
        var url = "/static/client/media/"+ data.time +".png";
        document.getElementById("wordcloud_pic").src = url;
        $("#wordcloud_pic").attr("alt",data.time);
        $('#wordcloud_pic').css('visibility','visible');
        $(".loading").fadeOut();
    });
}