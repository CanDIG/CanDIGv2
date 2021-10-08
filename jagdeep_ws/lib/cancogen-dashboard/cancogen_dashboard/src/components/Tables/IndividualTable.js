import React from 'react';
import PropTypes from 'prop-types';

import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-alpine.css';
import '../../assets/css/VariantsSearch.css';

function IndividualTable({ individualsRowData }) {
  const individualsColumnDefs = [
    { headerName: 'ID', field: 'id' },
    { headerName: 'Sex', field: 'sex' },
    { headerName: 'Ethnicity', field: 'ethnicity' },
    { headerName: 'Karyotypic Sex', field: 'karyotypic_sex' },
    { headerName: 'Height', field: 'height' },
    { headerName: 'Weight', field: 'weight' },
    { headerName: 'Education', field: 'education' },
  ];

  const individualsGridOptions = {
    defaultColDef: {
      editable: false,
      sortable: true,
      resizable: true,
      filter: true,
      flex: 1,
      minWidth: 20,
      minHeight: 300,
    },
    paginationAutoPageSize: true,
    pagination: true,
  };

  const extraFieldHandler = (results) => {
    const processedResults = [];

    if (results === undefined) {
      return []; // TODO: display a warning message
    }

    for (let i = 0; i < results.length; i += 1) {
      const tempObj = results[i];
      tempObj.height = results[i].extra_properties.height;
      tempObj.weight = results[i].extra_properties.height;
      tempObj.education = results[i].extra_properties.education;

      processedResults.push(tempObj);
    }

    return processedResults;
  };

  return (
    <>
      <div className="ag-theme-alpine">
        <AgGridReact
          columnDefs={individualsColumnDefs}
          rowData={extraFieldHandler(individualsRowData)}
          gridOptions={individualsGridOptions}
        />
      </div>

    </>
  );
}

IndividualTable.propTypes = {
  individualsRowData: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default IndividualTable;
