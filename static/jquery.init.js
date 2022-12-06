/* Puts the included jQuery into our own namespace using noConflict and passing
 * it 'true'. This ensures that the included jQuery doesn't pollute the global
 * namespace (i.e. this preserves pre-existing values for both window.$ and
 * window.jQuery).
 */
// var django = {
//     "jQuery": 
// };
// jQuery.noConflict()
 var Main={
            "is_debug":false,
            "dashboard": null,
            "table":null,
            "series_data":null

            };

 $(function() {
      Main.table = $("#table_trans");
    /* do not change this two statements */
       window.operateEvents = {
        'click .edit': function (e, value, row, index) {
            var my_url = "/api/record-detail/" + row.id;
            $.ajax({"method": "GET",
                    "url": my_url }).done(function( msg ) {
                                      $("#custom_form").html(msg);
                                      $("#custom_form_modal").modal("show");

                      });
        },
        'click .remove': function (e, value, row, index) {
            Main.table.bootstrapTable('remove', {
                                      field: 'id',
                                      values: [row.id]
                                      })
        }
      };
      $("#table_trans").bootstrapTable();
      /* do not change this two statements */

    $(".project_link").css({"cursor":"pointer"});
    $(".project_link").bind("click", function(e){
        var name = $(this).data("project");
        for(var i in Main.dashboard.series){
               var o = Main.dashboard.series[i];
               if(o.name == name){
                    if(o.visible){
                        $(this).removeClass("btn");
                        $(this).removeClass("btn-info");
                        o.hide();
                    }
                    else{
                        $(this).addClass("btn");
                        $(this).addClass("btn-info");
                        o.show();
                    }
               }

        }

    });

    $(".account_link").css({"cursor":"pointer"});
    $(".account_link").bind("click", function(e){
                 var account  =	$(this).data("account");
                 var my_url = "/api/trans";
                 $("#trans_title").html(account);
                 console.log(my_url);
                 $.ajax({ method: "POST",
		          data :  {"category": account, "context":"account"} ,
                          dataType: "json",
                          url: my_url }).done(function( msg ) {

                                  $("#table_trans").bootstrapTable('removeAll');
                                  $("#table_trans").bootstrapTable('load', msg["data"]);
                                  $("#trans_info").modal("show");

                  });


    });
    Main.submit_custom_form = function(my_url){

        console.log(my_url);
        var form_data = {};
        $("#custom_form .form-control").each(function(elem){
                                                form_data[$(this).attr("name")] = $(this).val()
                                             });
        console.log(form_data);
        $.ajax({ method: "POST",
		         data : form_data,
                 dataType: "json",
                 url: my_url }).done(function( msg ) {
                                Main.table.bootstrapTable('refresh');
                                $("#custom_form").modal("hide");
                            });
    };


	 // TODO add caching

	 Main["show_all7"] = function(){
                 var my_url = "/api/trans";
                 var date = new Date();
                 var days = 7;
                 var last = new Date(date.getTime() - (days * 24 * 60 * 60 * 1000));
                 var day = last.getDate();
                 var  dt = last.yyyymmdd();
                 $("#trans_title").html( dt);
                 console.log(my_url);
                 $.ajax({ method: "POST",
		                  data :  {"date": dt} ,
                          dataType: "json",
                          url: my_url }).done(function( msg ) {

                                  $("#table_trans").bootstrapTable('removeAll');
                                  $("#table_trans").bootstrapTable('load', msg["data"]);
                                  $("#trans_info").modal("show");

                  });

	 };
	 Main["show_all90"] = function(){
                 var my_url = "/api/trans";
                 var date = new Date();
                 var days = 7;
                 var last = new Date(date.getTime() - (days * 24 * 60 * 60 * 1000));
                 var day = last.getDate();
                 var  dt = last.yyyymmdd();
                 $("#trans_title").html( dt);
                 console.log(my_url);
                 $.ajax({ method: "POST",
		          data :  {"date": dt} ,
                          dataType: "json",
                          url: my_url }).done(function( msg ) {
                                  $("#table_trans").bootstrapTable('removeAll');
                                  $("#table_trans").bootstrapTable('load', msg["data"]);
                                  $("#trans_info").modal("show");

                  });

	 };
	 Main["current_object"] = null;
 	 Main["get_trans_q"] = function(q_id){
	 	 var my_url = "/api/trans_q/" + q_id;
		 $.ajax({ method: "GET",
			      dataType: "json",
			      url: my_url }).done(function( msg ) {
 								alert(msg)
 						     });
	 };

     Main["setposition"] = function(e, project, name, context, title) {
				     var bodyOffsets = document.body.getBoundingClientRect();
				     tempX = e.pageX - bodyOffsets.left;
				     tempY = e.pageY;
				     console.log(tempX);
			             $("#context_title").html(project + " " +title);
			             $("#project_title").html(project);
				     $("#xxx").show();
				     $("#xxx").data({ "context":context, "category": name, "project": project, "title": title});
				     $("#xxx").css({ 'top': tempY, 'left': tempX });
             };

	 Main["show_info"] = function(e){
		 var context  =	$("#xxx").data("context");
		 var project  =	$("#xxx").data("project");
		 var category = $("#xxx").data("category");
		 var title = $("#xxx").data("title");
                 $("#conv_title").html(title);
                 var my_url = "/api/common_info";
	             if(Main.is_debug)
		             my_url+="?html=1";
                 console.log(my_url);
	             console.log(e);
                 $.ajax({ method: "POST",
		          data :  {"project": project, "category": category,  "context": context} ,
			      dataType: "json",
			      url: my_url }).done(function( msg ) {
					     	   Main.current_object = msg;
						       Main.show_common_info(msg);
						     });

	 };

     Main["show_project"]= function(e){
		 var project  =	$("#xxx").data("project");
		 var title = $("#xxx").data("title");
                 $("#project_info_title").html(project);
		 var my_url = "/api/project/info"
                 $.ajax({ method: "POST",
		        data :  {"project": project} ,
			  dataType: "json",
			  url: my_url }).done(function( msg ) {
			  					Main.current_object = msg;
                                Main.draw_project_info(msg);

			});



	 };

     Main["project_operations"]= function(e){
		 		 var project  =	$("#xxx").data("project");

                 var my_url = "/api/trans";
		 		 var title = $("#xxx").data("title");
                 $("#trans_title").html(title);

                 console.log(my_url);

                 $.ajax({ method: "POST",
		          data :  {"category": project, "context":"project"} ,
			      dataType: "json",
			      url: my_url }).done(function( msg ) {
                                  $("#table_trans").bootstrapTable('removeAll');
                                  $("#table_trans").bootstrapTable('load', msg["data"]);
                                  $("#trans_info").modal("show");
                      });


         };
         Main["show_map"] = function(e){
		 var context  =	$("#xxx").data("context");
		 var project  =	$("#xxx").data("project");
		 var category = $("#xxx").data("category");
		 var url = "";
	         if(context == "account")
                    my_url = "/api/account_map";
		     else
                    my_url = "/api/contragent_map";

             console.log(my_url);
             $.ajax({ method: "POST",
		             data :  {"project": project, "category": category,  "context": context} ,
			         dataType: "json",
			         url: my_url }).done(function( msg ) {
               			  var name = $("#xxx").data("category");
               			  $("#map_info_title").html(name);
               			  Main.current_object = msg;
                          draw_account_map(msg);
			});

	};

	 Main["show_operation"] = function(e){

		 var context  =	$("#xxx").data("context");
		 var project  =	$("#xxx").data("project");
		 var category = $("#xxx").data("category");
         var my_url = "/api/trans_context";
		 var title = $("#xxx").data("title");
         $("#trans_title").html(title);

         console.log(my_url);
         $.ajax({ method: "POST",
		          data :  {"project": project, "category": category,  "context": context} ,
			      dataType: "json",
			      url: my_url }).done(function( msg ) {
                                  $("#table_trans").bootstrapTable('removeAll');
                                  $("#table_trans").bootstrapTable('load', msg["data"]);
                                  $("#trans_info").modal("show");

                 });
	};

function draw_account_map(msg){

    console.log(msg);
    var debits = [];
    var credits = [];
    for(var j in msg["categories"]){

      var i = msg["categories"][j];

      if(i in msg["credits"]){
          credits.push(msg["credits"][i].amnt);
      }else{
          credits.push(0);
      }

      if(i in msg["debits"]){
          debits.push(msg["debits"][i].amnt);
      }else{
         debits.push(0);
      }


    }

    Highcharts.chart('map_container', {

    chart: {
        polar: true,
        type: 'area'
    },

    accessibility: {
        description: ''
    },

    title: {
        text: 'расходы/приходы',
        x: -80
    },

    pane: {
        size: '80%'
    },

    xAxis: {
        categories: msg["categories"],
        tickmarkPlacement: 'on',
        lineWidth: 0
    },

    yAxis: {
        gridLineInterpolation: 'polygon',
        lineWidth: 0,
        min: 0
    },

    tooltip: {
        shared: true,
        pointFormat: '<span style="color:{series.color}">{series.name}: <b>${point.y:,.0f}</b><br/>'
    },

    legend: {
        align: 'right',
        verticalAlign: 'middle',
        layout: 'vertical'
    },

    series: [{
        name: 'Приходы ',
        data: debits,
        pointPlacement: 'on'
    }, {
        name: 'Расходы',
        data: credits,
        pointPlacement: 'on'
    }],

    responsive: {
        rules: [{
            condition: {
                maxWidth: 500
            },
            chartOptions: {
                legend: {
                    align: 'center',
                    verticalAlign: 'bottom',
                    layout: 'horizontal'
                },
                pane: {
                    size: '70%'
                }
            }
        }]
    }

  });

  $("#map_modal").modal("show");

};
Main["draw_project_info"]  = function(data){
	Highcharts.chart('ppie_head', {
	    chart: {
		plotBackgroundColor: null,
		plotBorderWidth: null,
		plotShadow: false,
		type: 'pie'
	    },
	    title: {
		text: 'Отношение расходов/приходов'
	    },
	    tooltip: {
		pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
	    },
	    accessibility: {
		point: {
		    valueSuffix: '%'
		}
	    },
	    plotOptions: {
		pie: {
		    allowPointSelect: true,
		    cursor: 'pointer',
		    dataLabels: {
		        enabled: true,
		        format: '<b>{point.name}</b>: {point.y:.1f} '
		    }
		}
	    },
	    series: [
	      {"name":"Общии расходы/приходы",
			"colorByPoint": true,

			data: [{
				name: "Расход",
				y: data["credit"],
				sliced: true,
				selected: true
			}, {
				name: 'Приходы',
				y: data["debit"]
			},]
	    }]


	});

	var common_income_credit = data["account_credit"];
	var common_income_credit_data = [];
	for(var i in common_income_credit){
		common_income_credit_data.push({"name":i,
		                                "y":common_income_credit[i]["amnt"] })

	}
	var common_income_debit = data["account_debit"];
	var common_income_debit_data = [];
	for(var i in common_income_debit){
		common_income_debit_data.push({"name":i,
		                               "y":common_income_debit[i]["amnt"] })

	}

	 //income by context
       Highcharts.chart('ppie1', {
	    chart: {
		plotBackgroundColor: null,
		plotBorderWidth: null,
		plotShadow: false,
		type: 'pie'
	    },
	    title: {
		text: 'Приходы'
	    },
	    tooltip: {
		pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
	    },
	    accessibility: {
		point: {
		    valueSuffix: '%'
		}
	    },
	    plotOptions: {
		pie: {
		    allowPointSelect: true,
		    cursor: 'pointer',
		    dataLabels: {
		        enabled: true,
		        format: '<b>{point.name}</b>: {point.y:.1f} '
		    }
		}
	    },
	    series: [
	      {"name":"Приходы",
		"colorByPoint": true,
		data:common_income_debit_data
	    }]


	});



	   //credit by context
	 Highcharts.chart('ppie2', {
	    chart: {
		plotBackgroundColor: null,
		plotBorderWidth: null,
		plotShadow: false,
		type: 'pie'
	    },
	    title: {
		text: 'расходы '
	    },
	    tooltip: {
		pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
	    },
	    accessibility: {
		point: {
		    valueSuffix: '%'
		}
	    },
	    plotOptions: {
		pie: {
		    allowPointSelect: true,
		    cursor: 'pointer',
		    dataLabels: {
		        enabled: true,
		        format: '<b>{point.name}</b>: {point.y:.1f} '
		    }
		}
	    },
	    series: [
	      {"name":"Общии расходы ",
		"colorByPoint": true,
		"data": common_income_credit_data
	    }]

	});
	var common_income_credit1 = data["contragent_credit"];
	var common_income_credit_data1 = []
	for(var i in common_income_credit1){
		common_income_credit_data1.push({"name":i, "y":common_income_credit1[i]["amnt"] })

	}
	var common_income_debit1 = data["contragent_debit"];
	var common_income_debit_data1 = []
	for(var i in common_income_debit1){
		common_income_debit_data1.push({"name":i, "y":common_income_debit1[i]["amnt"] })

	}

	 //income by context
       Highcharts.chart('ppie3', {
	    chart: {
		plotBackgroundColor: null,
		plotBorderWidth: null,
		plotShadow: false,
		type: 'pie'
	    },
	    title: {
		text: 'Приходы'
	    },
	    tooltip: {
		pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
	    },
	    accessibility: {
		point: {
		    valueSuffix: '%'
		}
	    },
	    plotOptions: {
		pie: {
		    allowPointSelect: true,
		    cursor: 'pointer',
		    dataLabels: {
		        enabled: true,
		        format: '<b>{point.name}</b>: {point.y:.1f} '
		    }
		}
	    },
	    series: [
	      {"name":"Приходы",
		"colorByPoint": true,
		"data":common_income_debit_data1
	    }]


	});



	   //credit by context
	 Highcharts.chart('ppie4', {
	    chart: {
		plotBackgroundColor: null,
		plotBorderWidth: null,
		plotShadow: false,
		type: 'pie'
	    },
	    title: {
		text: 'расходы '
	    },
	    tooltip: {
		pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
	    },
	    accessibility: {
		point: {
		    valueSuffix: '%'
		}
	    },
	    plotOptions: {
		pie: {
		    allowPointSelect: true,
		    cursor: 'pointer',
		    dataLabels: {
		        enabled: true,
		        format: '<b>{point.name}</b>: {point.y:.1f} '
		    }
		}
	    },
	    series: [
	      {"name":"Общии расходы ",
		"colorByPoint": true,
		"data": common_income_credit_data1
	    }]

	});

	$("#project_common_info").modal("show");
};
//common info show
Main["show_common_info"] = function(data){

    Highcharts.chart('pie_head', {
    chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
    },
    title: {
        text: 'Отношение расходов/приходов'
    },
    tooltip: {
        pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
    },
    accessibility: {
        point: {
            valueSuffix: '%'
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: false,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                format: '<b>{point.name}</b>: {point.y:.1f} '
            }
        },
        series:{
        	cursor: "pointer",
			point: {
				events: {
				  click: function(oEvent) {
				  	console.log(oEvent);
				  	console.log(this);
					var name = this.name;
					 //call function  with arguments
					Main.get_trans_q(this.q_id);
				  }
				}
			}

      }
    },
    series: [
      {"name":"Общии расходы/приходы",
        "colorByPoint": true,
        data: [{
            name: "Расход",
            y: data["credit"],
            q_id: data["credit_q_id"]
        }, {
            name: 'Приходы',
            y: data["debit"],
            q_id: data["debit_q_id"]

        },]
    }]


});

var common_income_credit = data["common_income_credit"];
common_income_credit_data = []
for(var i in common_income_credit){
	common_income_credit_data.push({"name":i, "y":common_income_credit[i]["amnt"] })

}
var common_income_debit = data["common_income_debit"];
common_income_debit_data = []
for(var i in common_income_debit){
	common_income_debit_data.push({"name":i, "y":common_income_debit[i]["amnt"] })

}

 //income by context
     Highcharts.chart('pie1', {
    chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
    },
    title: {
        text: 'Приходы'
    },
    tooltip: {
        pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
    },
    accessibility: {
        point: {
            valueSuffix: '%'
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                format: '<b>{point.name}</b>: {point.y:.1f} '
            }
        }
    },
    series: [
      {"name":"Приходы",
        "colorByPoint": true,
        data:common_income_debit_data
    }]


});



   //credit by context
    Highcharts.chart('pie2', {
    chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
    },
    title: {
        text: 'расходы '
    },
    tooltip: {
        pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
    },
    accessibility: {
        point: {
            valueSuffix: '%'
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                format: '<b>{point.name}</b>: {point.y:.1f} '
            }
        }
    },
    series: [
      {"name":"Общии расходы ",
        "colorByPoint": true,
        "data": common_income_credit_data
    }]


});

$("#common_info").modal("show");




};



function reload_dashwithfilters(){

    var contra = "";
	if($("#contragents_checkbox").prop("checked")){
            contra +="contragents=yes&";
	}else{
            contra +="contragents=no&";

	}
	if($("#accounts_checkbox").prop("checked")){
            contra +="accounts=yes";
	}else{
            contra +="accounts=no";

	}
	console.log(contra);
	window.location.href="/?"+contra;



};

$("#contragents_checkbox").bind("click", function(ev){
            reload_dashwithfilters();

	});
$("#accounts_checkbox").bind("click", function(ev){

            reload_dashwithfilters();

	});

Main.operateFormatter = function(value, row, index){
        return [
          '<a class="edit" href="javascript:void(0)" title="Like">',
          '<i class="bi bi-wrench"></i>',
          '</a>  ',
          '<a class="remove" href="javascript:void(0)" title="Remove">',
          '<i class="bi bi-x-octagon-fill"></i>',
          '</a>'
        ].join('')
};




Main.dashboard = Highcharts.chart('container', {
  chart: {
    type: 'packedbubble',
    height: '100%'
  },
  title: {
    text: 'Группировка по объему'

  },
  tooltip: {
    useHTML: true,
    pointFormat: '<b>{point.name}:</b> {point.value} тыс грн. оборот'
  },
  plotOptions: {
    packedbubble: {
      minSize: '1%',
      legend: {align: "left"},
      maxSize: '70%',
      zMin: 0,
      zMax: 1000,
      label: {enabled:true},
      layoutAlgorithm: {
        gravitationalConstant: 0.05,
        splitSeries: true,
        seriesInteraction: false,
        dragBetweenSeries: true,
        parentNodeLimit: true
      },
      dataLabels: {
        enabled: true,
        parentNodeFormat: '{series.name}',
        format: '{point.name}',
        filter: {
          property: 'y',
          operator: '>',
          value: 1
        },
        style: {
          color: 'black',
          textOutline: 'none',
          fontWeight: 'normal'
        }
      }



    }
  },
  events: {"afterAnimate": function(event){

				   console.log("upper");
				   console.log(event);

			}},
  series: Main.series_data,});

});