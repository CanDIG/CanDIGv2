import React, { useEffect, useReducer } from 'react';
import PropTypes from 'prop-types';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

import LoadingIndicator, { trackPromise, usePromiseTracker } from '../LoadingIndicator/LoadingIndicator';
import { fetchServers } from '../../api/api';

function reducer(state, action) {
  switch (action.type) {
    case 'addSeries':
      return {
        ...state,
        ...{
          series: [
            {
              data: action.payload,
              colorByPoint: true,
              showInLegend: false,
            }],
        },
      };
    case 'addCategories':
      return { ...state, ...{ xAxis: { categories: action.payload } } };
    default:
      throw new Error();
  }
}

/*
 * Component listing the server status in the form of bar graph
 */
function Server({ datasetId }) {
  const initialState = {
    credits: {
      enabled: false,
    },
    chart: {
      type: 'bar',
      height: '200px; auto',
    },
    title: {
      text: 'Server Status',
    },
    xAxis: {
      categories: [],
    },
    series: [
      {
        data: [],
      },
    ],
  };

  /*
   * chartOptions describes the format and style of the graph.
   * More information on Highcharts website
   */
  const [chartOptions, dispatchChartOptions] = useReducer(reducer, initialState);

  const { promiseInProgress } = usePromiseTracker();

  /*
  * Process json returned from API
  * @param {object} data
  */
  function processData(data) {
    const dataList = [];
    const categoriesList = Object.keys(data).filter((key) => {
      if (key === 'Valid response') {
        return false;
      }
      return true;
    }).map((key) => {
      dataList.push(data[key]);
      return key;
    });

    return [dataList, categoriesList];
  }

  /*
   * Fetch server status information from the server after the component is added to the DOM
   * and create the bar graph by changing the chartOptions state
   */
  useEffect(() => {
    trackPromise(fetchServers()
      .then((data) => {
        const [dataList, categoriesList] = processData(data.status);

        dispatchChartOptions({ type: 'addSeries', payload: dataList });
        dispatchChartOptions({ type: 'addCategories', payload: categoriesList });
      }));
  }, [datasetId]);

  return (
    <>
      {promiseInProgress === true ? (
        <LoadingIndicator />
      ) : (
        <div>
          <HighchartsReact highcharts={Highcharts} options={chartOptions} />
        </div>
      )}
    </>
  );
}

Server.propTypes = {
  datasetId: PropTypes.string.isRequired,
};

export default Server;
