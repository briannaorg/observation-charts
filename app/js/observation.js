(function($){

    // Default chart configuration
    var chartWidth = $('body').width();
    var chartHeight = $('body').height();
    var chartOptions = {
        size: {
            width: chartWidth,
            height: chartHeight,
        },
        scale: 6,
        data: {
            constellations: '/data/constellations.json',
            objects: '/data/objects.json',
            stars: '/data/starsHD.json'
        },
        stars: {
            magnitude: 14,
        },
        galaxies: {
            magnitude: 8
        },
        openclusters: {
            magnitude: 6
        },
        globularclusters: {
            magnitude: 8
        },
        planetarynebulas: {
            magnitude: 10,
        },
        brightnebulas: {
            magnitude: 10,
        }
    };

    // App State Events
    // ================
    

    // Set iOS/Android CSS as necessary
    if( /Android/i.test(navigator.userAgent) ) {
        $('head').append('<link href="lib/ratchet/css/ratchet-theme-android.css" rel="stylesheet">');
    } else if( /iPhone|iPad|iPod/i.test(navigator.userAgent) ) {
        $('head').append('<link href="lib/ratchet/css/ratchet-theme-ios.css" rel="stylesheet">');
    }
      
    // Intercept 'push' events to hide/show the chart as needed.
    window.addEventListener('push', function(e) {
      console.log("got push event");
      console.log(e);

      // If index.html is in the URL, make sure the chart is shown.
      if (e.detail.state.url.search('index.html')) {
          console.log("showing chart");
          $('#chart-content').show();
      } else  {
          console.log("hiding chart");
          $('#chart-content').hide();
      }

    });

    // Chart-changing events
    // =====================
    
    // FOR DEBUG PURPOSES
    function switchRatchetTheme(theme) {
        // Switch the CSS file
        $('#ratchet-theme').remove();
        $('head').append('<link id="ratchet-theme" rel="stylesheet" type="text/css" href="lib/ratchet/css/ratchet-theme-' + theme + '.css">');
    }
    
    // Change the Chart theme. 
    function switchChartTheme(theme) {
        // Remove/Add body classes for all non-chart elements
        $('body').removeClass(localStorage.getItem('chart-theme'));
        $('body').addClass(theme);

        // Switch the active chart theme control
        $('#chart-control-' + localStorage.getItem('chart-theme')).removeClass('active');
        $('#chart-control-' + theme).addClass('active');

        // Switch the CSS file
        $('#chart-theme-' + localStorage.getItem('chart-theme')).remove();
        $('head').append('<link id="chart-theme-' + theme +'" rel="stylesheet" type="text/css" href="css/chart-' + theme + '.css">');

        // Store the new theme.
        localStorage.setItem('chart-theme', theme);
    }
    
    // The day theme control
    $('#chart-control-day').click(function(e) {
        switchChartTheme('day');
    });
    // The night theme control
    $('#chart-control-night').click(function(e) {
        switchChartTheme('night');
    });


    // Restore State/Configuration/Theme
    // =============
    
    // Restore theme from localstorage
    if ('chart-theme' in localStorage) {
        $('#chart-control-' + localStorage.getItem('chart-theme')).trigger('click');
    } else {
        $('#chart-control-day').trigger('click');
    }
    

    // Draw the chart.
    $('#chart-content').observationChart(chartOptions);
    $('#chart-content').on('drawn', function(e) {
        console.log("drawn");
    });


})(jQuery);

