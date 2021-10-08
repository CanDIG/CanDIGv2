import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

window.Highcharts = Highcharts;

/*
 * Transform a camelCase string to a capital spaced string
 */
function splitString(newString) {
  const splitted = newString.replace(/([a-z])([A-Z])/g, '$1 $2');
  const capitalized = splitted.charAt(0).toUpperCase() + splitted.substr(1);
  return capitalized;
}

/*
 * Component for offline chart
 * @param {string} chartType
 * @param {string} barTitle
 * @param {string} height
 * @param {string} datasetName
 * @param {array} dataObject
 */
function CustomOfflineChart({
  chartType,
  barTitle,
  height,
  datasetName,
  dataObject,
}) {
  const [chartOptions, setChartOptions] = useState({
    credits: {
      enabled: false,
    },
    chart: { type: chartType, height },
    title: {
      text: `Distribution of ${splitString(barTitle)}`,
    },
    subtitle: {
      text: datasetName,
    },
  });

  useEffect(() => {
    /*
     * Create a Pie chart from props
     */

    function createPieChart() {
      const options = {
        credits: {
          enabled: false,
        },
        chart: {
          plotBackgroundColor: null,
          plotBorderWidth: null,
          plotShadow: false,
        },
      };
      options.series = [
        {
          data: Object.keys(dataObject).map((key) => ({
            name: key,
            y: dataObject[key],
          })),
        },
      ];
      setChartOptions(options);
    }

    /*
     * Create Bar chart from props
     */
    function createBarChart() {
      const data = [];

      const categories = Object.keys(dataObject).map((key) => {
        data.push(dataObject[key]);
        return key;
      });

      setChartOptions({
        credits: {
          enabled: false,
        },
        series: [{ data, colorByPoint: true, showInLegend: false }],
        xAxis: { categories },
      });
    }

    if (chartType === 'pie') {
      createPieChart();
    } else {
      createBarChart();
    }
  }, [datasetName, dataObject, chartType]);

  return (
    <div>
      <HighchartsReact highcharts={Highcharts} options={chartOptions} />
    </div>
  );
}

CustomOfflineChart.propTypes = {
  chartType: PropTypes.string.isRequired,
  barTitle: PropTypes.string.isRequired,
  height: PropTypes.string,
  datasetName: PropTypes.string,
  dataObject: PropTypes.objectOf(PropTypes.number).isRequired,
};

CustomOfflineChart.defaultProps = {
  datasetName: '',
  height: '200px; auto',
};

export default CustomOfflineChart;
