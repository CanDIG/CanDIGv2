import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import HighchartsMore from 'highcharts/highcharts-more';

HighchartsMore(Highcharts);

function getPercentile(data, percentile) {
  data.sort();
  const index = (percentile / 100) * data.length;
  let result;
  if (Math.floor(index) === index) {
    result = (data[index - 1] + data[index]) / 2;
  } else {
    result = data[Math.floor(index)];
  }
  return result;
}

function getBoxValues(data) {
  const boxValues = [];
  data.sort();
  boxValues.push(Math.min(...data));
  boxValues.push(getPercentile(data, 25));
  boxValues.push(getPercentile(data, 50));
  boxValues.push(getPercentile(data, 75));
  boxValues.push(Math.max(...data));

  return boxValues;
}

function BoxPlotChart({ chartTitle, plotObject }) {
  const [chartOptions, setChartOptions] = useState({
    chart: {
      type: 'boxplot',
    },
    title: {
      text: chartTitle,
    },
    legend: {
      enabled: true,
    },
    plotOptions: {
      boxPlot: {
        boxDashStyle: 'Dash',
        fillColor: '#F0F0E0',
        lineWidth: 2,
        medianColor: '#0C5DA5',
        medianDashStyle: 'ShortDot',
        medianWidth: 3,
        stemColor: '#A63400',
        stemDashStyle: 'dot',
        stemWidth: 1,
        whiskerColor: '#3D9200',
        whiskerLength: '20%',
        whiskerWidth: 3,
      },
    },
  });

  useEffect(() => {
    const data = [];
    const categories = Object.keys(plotObject).map((key) => {
      data.push(getBoxValues(plotObject[key]));

      return key;
    });

    setChartOptions({
      xAxis: { categories },
      series: [{ data }],
    });
  }, [plotObject]);

  return (
    <div>
      <HighchartsReact highcharts={Highcharts} options={chartOptions} />
    </div>
  );
}

BoxPlotChart.propTypes = {
  chartTitle: PropTypes.string.isRequired,
  plotObject: PropTypes.objectOf(PropTypes.array).isRequired,
};

export default BoxPlotChart;
