import React, {
  useState, forwardRef, useRef, useEffect,
} from 'react';
import PropTypes from 'prop-types';

import {
  Row, Button, ButtonDropdown, DropdownToggle,
  InputGroup, InputGroupAddon, DropdownMenu,
  InputGroupText, Col, DropdownItem,
} from 'reactstrap';

import Style from '../../assets/css/StyledComponents/ColumnControlStyled';
import ClinMetadataDropdown from '../Dropdowns/ClinMetadataDropdown';
import { GlobalFilter } from '../Filters/filters';

const IndeterminateButton = forwardRef(
  ({ indeterminate, ...rest }, ref) => {
    const defaultRef = useRef();
    const resolvedRef = ref || defaultRef;

    useEffect(() => {
      resolvedRef.current.indeterminate = indeterminate;
    }, [resolvedRef, indeterminate]);

    return <Button ref={resolvedRef} {...rest} />;
  },
);

IndeterminateButton.propTypes = {
  indeterminate: PropTypes.bool,
};
IndeterminateButton.defaultProps = {
  indeterminate: false,
};

function DataControl({
  metadataCallback, toggleHideAllColumns,
  preGlobalFilteredRows, setGlobalFilter, state, allColumns,
  toggleRowFilter, toggleRowAggregation, isActiveMetadataDropdown,
}) {
  const [dropdownAdvOpen, setAdvOpen] = useState(false);
  const toggleDropdownAdv = () => setAdvOpen(!dropdownAdvOpen);
  const [dropdownColOpen, setColOpen] = useState(false);
  const toggleDropdownCol = () => setColOpen(!dropdownColOpen);

  const displayName = (id) => {
    const capitalized = (id.charAt(0).toLocaleUpperCase() + id.slice(1));
    return [...capitalized.matchAll(/[A-Z]{1}[a-z]*/g)].join(' ');
  };

  return (
    <>
      <Style>
        <Row>
          <Col>
            <InputGroup>
              <InputGroupAddon className="dataControl" addonType="prepend">
                <ClinMetadataDropdown className="dataDropdown" metadataCallback={metadataCallback} isActive={isActiveMetadataDropdown} />

                <IndeterminateButton className="toggleAll" onClick={() => toggleHideAllColumns()}> Toggle all </IndeterminateButton>
                <ButtonDropdown className="toggleColumn" isOpen={dropdownColOpen} toggle={toggleDropdownCol}>
                  <DropdownToggle caret>
                    Hide Columns
                  </DropdownToggle>
                  <DropdownMenu>
                    {allColumns.map((column) => (
                      <DropdownItem
                        onClick={() => column.toggleHidden()}
                        key={column.id}
                        active={column.isVisible}
                      >
                        {' '}
                        {displayName(column.id)}
                        {' '}
                      </DropdownItem>
                    ))}
                  </DropdownMenu>

                </ButtonDropdown>

                <ButtonDropdown className="toggleAdvanced" isOpen={dropdownAdvOpen} toggle={toggleDropdownAdv}>
                  <DropdownToggle caret>
                    Advanced
                  </DropdownToggle>
                  <DropdownMenu>
                    <DropdownItem onClick={toggleRowFilter}>Row Filters</DropdownItem>
                    <DropdownItem onClick={toggleRowAggregation}>Row Aggregation</DropdownItem>
                  </DropdownMenu>
                </ButtonDropdown>

                <InputGroupText className="globalSearchText">Search:</InputGroupText>
              </InputGroupAddon>
              <GlobalFilter
                className="globalSearchBar"
                preGlobalFilteredRows={preGlobalFilteredRows}
                globalFilter={state.globalFilter || ''}
                setGlobalFilter={setGlobalFilter}
              />
            </InputGroup>
          </Col>
        </Row>
        <Row />
        <Row>
          <Col />
        </Row>

      </Style>
    </>
  );
}

DataControl.propTypes = {
  metadataCallback: PropTypes.func,
  toggleHideAllColumns: PropTypes.func,
  preGlobalFilteredRows: PropTypes.arrayOf(PropTypes.object),
  setGlobalFilter: PropTypes.func,
  state: PropTypes.shape({
    globalFilter: PropTypes.func,
  }),
  allColumns: PropTypes.arrayOf(PropTypes.object),
  toggleRowFilter: PropTypes.func,
  toggleRowAggregation: PropTypes.func,
  isActiveMetadataDropdown: PropTypes.bool,

};
DataControl.defaultProps = {
  metadataCallback: () => {},
  toggleHideAllColumns: () => {},
  preGlobalFilteredRows: [],
  setGlobalFilter: () => {},
  state: {},
  allColumns: [],
  toggleRowFilter: () => {},
  toggleRowAggregation: () => {},
  isActiveMetadataDropdown: false,
};

export default DataControl;
