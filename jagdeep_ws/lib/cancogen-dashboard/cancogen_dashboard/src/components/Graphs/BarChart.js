import React, { useReducer, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

import LoadingIndicator, { trackPromise, usePromiseTracker } from '../LoadingIndicator/LoadingIndicator';
import { notify, NotificationAlert } from '../../utils/alert';
import { getCountsFederation } from '../../api/api';
import { mergeFederatedResults } from '../../utils/utils';

// Hook
// Used to keep the previous value of a state or prop
function usePrevious(value) {
  const ref = useRef();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}

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
 * Component for bar chart graphs
 * @param {string} datasetId
 * @param {string} table
 * @param {string} field
 * @param {string} title
 */
function BarChart({
  datasetId, table, field, title,
}) {
  const initialState = {
    credits: {
      enabled: false,
    },
    chart: {
      type: 'bar',
      height: '200px; auto',
    },
    title: {
      text: title,
    },
    xAxis: {
      categories: [],
    },
    series: [
      {
        colorByPoint: true,
        showInLegend: false,
        data: [],
      },
    ],
  };

  const [chartOptions, dispatchChartOptions] = useReducer(reducer, initialState);
  const { promiseInProgress } = usePromiseTracker();
  const prevDatasetId = usePrevious(datasetId);
  const notifyEl = useRef(null);

  /*
  * Process json returned from API
  * @param {object} data
  */
  function processCounts(data) {
    const categories = [];
    const dataList = Object.keys(data).map((key) => {
      categories.push(
        key.charAt(0).toUpperCase() + key.slice(1),
      );
      return data[key];
    });

    return [categories, dataList];
  }

  /*
  * Create the graph object by dispatching lists to reducer
  * @param {list} dataList
  * @param {list} categories
  */
  function createChart(dataList, categories) {
    dispatchChartOptions({ type: 'addSeries', payload: dataList });
    dispatchChartOptions({ type: 'addCategories', payload: categories });
  }

  useEffect(() => {
    if (prevDatasetId !== datasetId && datasetId) {
      trackPromise(getCountsFederation(datasetId, table, field)
        .then((data) => {
          if (!data.results[0].results[table][0]) {
            throw new Error();
          }
          const merged = mergeFederatedResults(data);
          const [categories, dataList] = processCounts(merged[0][table][0][field]);
          createChart(dataList, categories);
        }).catch(() => {
          createChart([], []);
          notify(
            notifyEl,
            'Some resources you requested were not available.',
            'warning',
          );
        }));
    }
  });
  return (
    <>
      <NotificationAlert ref={notifyEl} />
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

BarChart.propTypes = {
  datasetId: PropTypes.string.isRequired,
  table: PropTypes.string.isRequired,
  field: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
};

export default BarChart;
