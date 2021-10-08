import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { trackPromise, usePromiseTracker } from 'react-promise-tracker';

import BASE_URL from '../constants/constants';
import ClinMetadataTable from '../components/Tables/ClinMetadataTable';
import LoadingIndicator from '../components/LoadingIndicator/LoadingIndicator';
import { notify, NotificationAlert } from '../utils/alert';
import { tableSchema } from '../constants/tableSchemaFilters';

function CreateColumns(columnNames, setColumnState, columnSchema) {
  const columnList = [];

  const displayName = (id) => {
    const capitalized = (id.charAt(0).toLocaleUpperCase() + id.slice(1));
    return [...capitalized.matchAll(/[A-Z]{1}[a-z]*/g)].join(' ');
  };

  Object.values(columnNames).forEach((name) => {
    if (columnSchema[name].active) {
      const column = {
        Header: displayName(name),
        accessor: name,
        Filter: columnSchema[name].Filter,
        hidden: columnSchema[name].hidden,
        aggregate: 'count',
        Aggregated: ({ value }) => `${value} `,
      };
      columnList.push(column);
    }
  });
  setColumnState(columnList);
}

function TableApp({ datasetId }) {
  const [selectedMetadata, setSelectedMetadata] = useState('patients');
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);

  const { promiseInProgress } = usePromiseTracker();

  const notifyEl = useRef(null);

  React.useEffect(() => {
    // fetch data
    try {
      const datasets = [];
      if (datasetId) {
        trackPromise(
          fetch(`${BASE_URL}/${selectedMetadata}/search`, {
            method: 'POST',
            body: JSON.stringify({ datasetId }),
            headers: {
              'Content-Type': 'application/json',
            },
          })
            .then((response) => {
              if (response.ok) {
                return response.json();
              }
              return {};
            })
            .then((dataResponse) => {
              for (let i = 0; i < dataResponse.results[selectedMetadata].length; i += 1) {
                datasets.push(dataResponse.results[selectedMetadata][i]);
              }
              setData(datasets);
              CreateColumns(Object.keys(datasets[0]), setColumns, tableSchema[selectedMetadata]);
            })
            .catch(() => {
              notify(
                notifyEl,
                'The resources you requested were not available.',
                'warning',
              );
            }),
        );
      }
    } catch (err) {
      notify(
        notifyEl,
        'The resources you requested were not available.',
        'warning',
      );
    }
  }, [selectedMetadata, datasetId]);

  const dataM = React.useMemo(() => data, [data]);
  const columnsM = React.useMemo(() => columns, [columns]);

  return (
    <div className="content">
      {promiseInProgress === true ? (
        <LoadingIndicator />
      ) : (
        <>
          <NotificationAlert ref={notifyEl} />
          <ClinMetadataTable
            columns={columnsM}
            data={dataM}
            metadataCallback={setSelectedMetadata}
            isActiveMetadataDropdown
            setActiveID={() => {}}
            isMainTable

          />
        </>
      )}
    </div>
  );
}

TableApp.propTypes = {
  datasetId: PropTypes.string,
};
TableApp.defaultProps = {
  datasetId: 'patients',
};

export default TableApp;
