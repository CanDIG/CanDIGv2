import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  useTable, useSortBy, usePagination, useFilters,
  useGlobalFilter, useGroupBy, useExpanded,
} from 'react-table';

// reactstrap components
import { Row } from 'reactstrap';
import Styles from '../../assets/css/StyledComponents/TableStyled';
import { DefaultColumnFilter, FuzzyTextFilterFn, SelectColumnFilter } from '../Filters/filters';

import PaginationBar from './Pagination';
import DataControl from './DataControls';

FuzzyTextFilterFn.autoRemove = (val) => !val;

function TableHeader({ headerGroups, getColumnSortSymbol, getGroupedSymbol }) {
  return (
    <thead>
      {headerGroups.map((headerGroup) => (
        <tr {...headerGroup.getHeaderGroupProps()}>
          {headerGroup.headers.map((column) => (
            <th scope="row" {...column.getHeaderProps()} className={column.id}>
              <table>
                <tbody>
                  <tr>
                    <th>
                      {column.canGroupBy ? (
                      // If the column can be grouped, add a toggle
                        <div>

                          <span {...column.getGroupByToggleProps()}>
                            {getGroupedSymbol(column)}
                          </span>
                        </div>
                      ) : null}
                    </th>
                    <th>
                      <div>
                        <span {...column.getSortByToggleProps()}>
                          {column.render('Header')}
                        </span>
                      </div>
                    </th>
                    <th>
                      <div>
                        <span>
                          {/* Add a sort direction indicator */}
                          {getColumnSortSymbol(column)}
                        </span>
                      </div>
                    </th>
                  </tr>
                </tbody>
              </table>

              {/* Render the columns filter UI */}
              <div>{column.canFilter ? column.render('Filter') : null}</div>
            </th>

          ))}
        </tr>

      ))}
    </thead>
  );
}

TableHeader.propTypes = {
  headerGroups: PropTypes.arrayOf(PropTypes.object),
  getColumnSortSymbol: PropTypes.func,
  getGroupedSymbol: PropTypes.func,
};

TableHeader.defaultProps = {
  headerGroups: [],
  getColumnSortSymbol: () => {},
  getGroupedSymbol: () => {},
};

function ClinMetadataTable({
  columns, data, metadataCallback, isActiveMetadataDropdown, setActiveID, isMainTable,
}) {
  const filterTypes = React.useMemo(
    () => ({
      // Add a new fuzzyTextFilterFn filter type.
      fuzzyText: FuzzyTextFilterFn,
      text: (rows, id, filterValue) => rows.filter((row) => {
        const rowValue = row.values[id];
        return rowValue !== undefined
          ? String(rowValue)
            .toLowerCase()
            .startsWith(String(filterValue).toLowerCase())
          : true;
      }),
      select: SelectColumnFilter,
    }),
    [],
  );

  const defaultColumn = React.useMemo(
    () => ({
      // Set up our default Filter UI
      Filter: DefaultColumnFilter,

    }),
    [],
  );

  const {
    getTableProps, getTableBodyProps, headerGroups, prepareRow,
    allColumns, toggleHideAllColumns, state, page,
    canPreviousPage, canNextPage, pageOptions, pageCount,
    gotoPage, nextPage, previousPage, setPageSize, preGlobalFilteredRows,
    setGlobalFilter,
    state: { pageIndex, pageSize },
  } = useTable({
    columns,
    data,
    initialState: {
      pageIndex: 0,
      hiddenColumns: columns.filter((column) => column.hidden).map((column) => column.accessor),
    },
    filterTypes,
    defaultColumn,

  },
  useFilters, useGlobalFilter, useGroupBy,
  useSortBy, useExpanded, usePagination);

  const [rowFilterVisible, setRowFilterVisible] = useState(true);

  function toggleRowFilterVisible() {
    setRowFilterVisible(!rowFilterVisible);
  }

  const [rowAggregationVisible, setRowAggregationVisible] = useState(true);

  function toggleRowAggregationVisible() {
    setRowAggregationVisible(!rowAggregationVisible);
  }

  function getColumnSortSymbol(column) {
    if (column.isSorted) {
      if (column.isSortedDesc) {
        return (
          <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-sort-alpha-down-alt" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M4 2a.5.5 0 0 1 .5.5v11a.5.5 0 0 1-1 0v-11A.5.5 0 0 1 4 2z" />
            <path fillRule="evenodd" d="M6.354 11.146a.5.5 0 0 1 0 .708l-2 2a.5.5 0 0 1-.708 0l-2-2a.5.5 0 0 1 .708-.708L4 12.793l1.646-1.647a.5.5 0 0 1 .708 0z" />
            <path d="M9.027 7h3.934v-.867h-2.645v-.055l2.567-3.719v-.691H9.098v.867h2.507v.055L9.027 6.309V7zm.637 7l.418-1.371h1.781L12.281 14h1.121l-1.78-5.332h-1.235L8.597 14h1.067zM11 9.687l.652 2.157h-1.351l.652-2.156H11z" />
          </svg>
        );
      }
      return (
        <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-sort-alpha-up" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M4 14a.5.5 0 0 0 .5-.5v-11a.5.5 0 0 0-1 0v11a.5.5 0 0 0 .5.5z" />
          <path fillRule="evenodd" d="M6.354 4.854a.5.5 0 0 0 0-.708l-2-2a.5.5 0 0 0-.708 0l-2 2a.5.5 0 1 0 .708.708L4 3.207l1.646 1.647a.5.5 0 0 0 .708 0z" />
          <path d="M9.664 7l.418-1.371h1.781L12.281 7h1.121l-1.78-5.332h-1.235L8.597 7h1.067zM11 2.687l.652 2.157h-1.351l.652-2.157H11zM9.027 14h3.934v-.867h-2.645v-.055l2.567-3.719v-.691H9.098v.867h2.507v.055l-2.578 3.719V14z" />
        </svg>
      );
    }
    return ('');
  }

  function getGroupedSymbol(column) {
    return (
      column.isGrouped
        ? (
          <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-x-square-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm3.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z" />
          </svg>
        )
        : (
          <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-layout-text-sidebar-reverse" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M2 1h12a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zm12-1a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h12z" />
            <path fillRule="evenodd" d="M5 15V1H4v14h1zm8-11.5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5zm0 3a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5zm0 3a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5zm0 3a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5z" />
          </svg>
        )
    );
  }

  function getCellStyle(cell) {
    if (cell.isGrouped) {
      return ({ background: '#0aff0082' });
    } if (cell.isAggregated) {
      return ({ background: '#ffa50078' });
    } if (cell.isPlaceholder) {
      return ({ background: '#ff000042' });
    }
    return ({ });
  }

  function handleAggregation(cell, row) {
    if (cell.isGrouped) {
      return (
        <>
          <span {...row.getToggleRowExpandedProps()}>
            {row.isExpanded ? (
              <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-arrows-collapse" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 0 1h-13A.5.5 0 0 1 1 8zm7-8a.5.5 0 0 1 .5.5v3.793l1.146-1.147a.5.5 0 0 1 .708.708l-2 2a.5.5 0 0 1-.708 0l-2-2a.5.5 0 1 1 .708-.708L7.5 4.293V.5A.5.5 0 0 1 8 0zm-.5 11.707l-1.146 1.147a.5.5 0 0 1-.708-.708l2-2a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1-.708.708L8.5 11.707V15.5a.5.5 0 0 1-1 0v-3.793z" />
              </svg>
            )
              : (
                <svg width="1em" height="1em" viewBox="0 0 16 16" className="bi bi-arrows-expand" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 0 1h-13A.5.5 0 0 1 1 8zM7.646.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1-.708.708L8.5 1.707V5.5a.5.5 0 0 1-1 0V1.707L6.354 2.854a.5.5 0 1 1-.708-.708l2-2zM8 10a.5.5 0 0 1 .5.5v3.793l1.146-1.147a.5.5 0 0 1 .708.708l-2 2a.5.5 0 0 1-.708 0l-2-2a.5.5 0 0 1 .708-.708L7.5 14.293V10.5A.5.5 0 0 1 8 10z" />
                </svg>
              )}
          </span>
          {' '}
          {cell.render('Cell')}
          {' '}
          (
          {row.subRows.length}
          )
        </>
      );
    } if (cell.isAggregated) {
      return cell.render('Aggregated');
    } if (cell.isPlaceholder) {
      return null;
    }
    return cell.render('Cell');
  }

  return (
    <>

      {data.length > 0
        ? (
          <>
            <DataControl
              metadataCallback={metadataCallback}
              toggleHideAllColumns={toggleHideAllColumns}
              preGlobalFilteredRows={preGlobalFilteredRows}
              setGlobalFilter={setGlobalFilter}
              state={state}
              allColumns={allColumns}
              toggleRowFilter={toggleRowFilterVisible}
              toggleRowAggregation={toggleRowAggregationVisible}
              isActiveMetadataDropdown={isActiveMetadataDropdown}
            />

            <Row>

              <Styles rowFilter={rowFilterVisible} rowAggregation={rowAggregationVisible}>
                <table {...getTableProps()} className={isMainTable ? 'mainTable' : 'subTable'}>
                  <TableHeader
                    headerGroups={headerGroups}
                    getColumnSortSymbol={getColumnSortSymbol}
                    getGroupedSymbol={getGroupedSymbol}
                  />
                  <tbody {...getTableBodyProps()}>
                    {page.map((row) => {
                      prepareRow(row);
                      return (
                        <tr {...row.getRowProps()} onClick={() => { setActiveID(row.values.ID); }}>
                          {row.cells.map((cell) => (
                            <td
                              {...cell.getCellProps()}
                              style={getCellStyle(cell)}
                            >
                              {handleAggregation(cell, row)}
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </Styles>
            </Row>

            <PaginationBar
              canPreviousPage={canPreviousPage}
              canNextPage={canNextPage}
              pageOptions={pageOptions}
              pageCount={pageCount}
              gotoPage={gotoPage}
              nextPage={nextPage}
              previousPage={previousPage}
              setPageSize={setPageSize}
              pageSize={pageSize}
              pageIndex={pageIndex}
            />
          </>
        )
        : <></>}

    </>
  );
}

ClinMetadataTable.propTypes = {
  columns: PropTypes.arrayOf(PropTypes.object),
  data: PropTypes.arrayOf(PropTypes.object),
  metadataCallback: PropTypes.func,
  isActiveMetadataDropdown: PropTypes.bool,
  setActiveID: PropTypes.func,
  isMainTable: PropTypes.bool,
};
ClinMetadataTable.defaultProps = {
  columns: [],
  data: [],
  metadataCallback: () => {},
  isActiveMetadataDropdown: false,
  isMainTable: false,
  setActiveID: () => {},

};

export default ClinMetadataTable;
