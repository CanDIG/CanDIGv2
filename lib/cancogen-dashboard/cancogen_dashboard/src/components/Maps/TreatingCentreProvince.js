import React, { useReducer, useEffect, useRef } from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import HighchartsMap from 'highcharts/modules/map';
import mapDataCanada from '@highcharts/map-collection/countries/ca/ca-all.geo.json';
import PropTypes from 'prop-types';

import LoadingIndicator, { trackPromise, usePromiseTracker } from '../LoadingIndicator/LoadingIndicator';
import { notify, NotificationAlert } from '../../utils/alert';
import { getCountsFederation } from '../../api/api';
import { mergeFederatedResults } from '../../utils/utils';

// Initialize HighchartsMap
HighchartsMap(Highcharts);

const initialState = {
  title: {
    text: 'Treating Centre Province',
  },
  credits: {
    enabled: false,
  },
  legend: {
    layout: 'vertical',
    align: 'right',
    verticalAlign: 'middle',
  },
  colorAxis: {
    min: 0,
    minColor: '#E6E7E8',
    maxColor: '#005645',
  },
  series: [
    {
      type: 'map',
      name: 'Province',
      mapData: mapDataCanada,
      states: {
        hover: {
          color: '#BADA55',
        },
      },
      dataLabels: {
        enabled: false,
        format: '{point.name}',
      },
    },
  ],
};

// Highcharts Map requires a specific set of codes for provinces
// and territories, as represented by hcProvCodes below.
const hcProvCodes = [
  'ca-ab', 'ca-bc', 'ca-mb', 'ca-nb', 'ca-nl', 'ca-nt', 'ca-ns',
  'ca-nu', 'ca-on', 'ca-pe', 'ca-qc', 'ca-sk', 'ca-yt'];
const provShortCodes = ['AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'];
const provFullNames = [
  'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
  'Northwest Territories', 'Nova Scotia', 'Nunavut', 'Ontario', 'Prince Edward Island',
  'Quebec', 'Saskatchewan', 'Yukon Territory'];

function reducer(state, action) {
  switch (action.type) {
    case 'addSeries':
      return {
        ...state,
        ...{
          series: [
            {
              data: action.payload,
              type: 'map',
              name: 'Province',
              mapData: mapDataCanada,
              states: {
                hover: {
                  color: '#BADA55',
                },
              },
              dataLabels: {
                enabled: false,
                format: '{point.name}',
              },
            },
          ],
        },
      };
    default:
      throw new Error();
  }
}

function TreatingCentreProvince({ datasetId }) {
  const { promiseInProgress } = usePromiseTracker();
  const [chartOptions, dispatchChartOptions] = useReducer(reducer, initialState);
  const notifyEl = useRef(null);

  function processJson(data) {
    const dataCount = [];
    Object.keys(data).forEach((name) => {
      if (provShortCodes.includes(name)) {
        const tempDataCount = [];
        tempDataCount.push(hcProvCodes[provShortCodes.indexOf(name)]);
        tempDataCount.push(data[name]);
        dataCount.push(tempDataCount);
      } else if (provFullNames.includes(name)) {
        const tempDataCount = [];
        tempDataCount.push(hcProvCodes[provFullNames.indexOf(name)]);
        tempDataCount.push(data[name]);
        dataCount.push(tempDataCount);
      }
    });

    return dataCount;
  }

  useEffect(() => {
    // Mimic the didUpdate function
    try {
      if (datasetId) {
        trackPromise(
          getCountsFederation(datasetId, 'enrollments', 'treatingCentreProvince')
            .then((data) => {
              let dataCount;

              if (data) {
                if (!data.results[0].enrollments[0]) {
                  throw new Error();
                }
                const merged = mergeFederatedResults(data);
                const { treatingCentreProvince } = merged[0].enrollments[0];

                dataCount = processJson(treatingCentreProvince);
              }
              dispatchChartOptions({ type: 'addSeries', payload: dataCount });
            }).catch(() => {
              notify(
                notifyEl,
                'Some resources you requested were not available.',
                'warning',
              );
              dispatchChartOptions({ type: 'addSeries', payload: [] });
            }),
        );
      }
    } catch (err) {
      console.log(err);
    }
  }, [datasetId]);

  return (
    <>
      <NotificationAlert ref={notifyEl} />
      {promiseInProgress === true ? (
        <LoadingIndicator />
      ) : (
        <div>
          <HighchartsReact
            contructorType="mapChart"
            highcharts={Highcharts}
            options={chartOptions}
          />
        </div>
      )}
    </>
  );
}

TreatingCentreProvince.propTypes = {
  datasetId: PropTypes.string.isRequired,
};

export default TreatingCentreProvince;
