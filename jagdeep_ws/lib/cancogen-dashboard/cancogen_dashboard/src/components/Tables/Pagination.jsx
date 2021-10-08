import React, { useState } from 'react';
import PropTypes from 'prop-types';

// reactstrap components
import {
  Button, InputGroup, InputGroupAddon,
  Input, InputGroupText, InputGroupButtonDropdown, DropdownToggle,
  DropdownMenu, DropdownItem,
} from 'reactstrap';
import PaginationStyle from '../../assets/css/StyledComponents/PaginationStyled';

function PaginationBar({
  gotoPage, previousPage, nextPage, canPreviousPage,
  canNextPage, pageOptions, pageIndex, pageSize,
  pageCount, setPageSize,

}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const toggleDropDown = () => setDropdownOpen(!dropdownOpen);

  return (
    <div className="pagination">
      <PaginationStyle>
        <InputGroup>
          <InputGroupAddon className="pageControls" addonType="prepend">
            <Button onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
              &lt; &lt;
            </Button>
            <Button onClick={() => previousPage()} disabled={!canPreviousPage}>
              &lt;
            </Button>
            <Button onClick={() => nextPage()} disabled={!canNextPage}>
              &gt;
            </Button>
            <Button onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
              &gt;&gt;
            </Button>
            <InputGroupText className="pageCountOuter">
              Page
              {' '}
              <strong className="pageCountBox">
                {pageIndex + 1}
                {' '}
                of
                {' '}
                {pageOptions.length}
              </strong>
            </InputGroupText>
            <InputGroupText className="goToPage">
              Go to page:
            </InputGroupText>
          </InputGroupAddon>
          <Input
            className="tablePageInput"
            type="number"
            defaultValue={pageIndex + 1}
            onChange={(e) => {
              const pageCounter = e.target.value ? Number(e.target.value) - 1 : 0;
              gotoPage(pageCounter);
            }}
          />
          <InputGroupButtonDropdown addonType="append" isOpen={dropdownOpen} toggle={toggleDropDown}>
            <DropdownToggle
              caret
              style={{
                marginTop: '0%',
                marginBottom: '0%',
                marginLeft: '0%',
              }}
            >
              Show
              {' '}
              {pageSize}
            </DropdownToggle>
            <DropdownMenu onClick={(e) => {
              setPageSize(Number(e.target.value));
            }}
            >
              {[10, 20, 30, 40, 50].map((rowCount) => (
                <DropdownItem
                  key={rowCount}
                  value={rowCount}
                >
                  Show
                  {' '}
                  {rowCount}
                </DropdownItem>
              ))}
            </DropdownMenu>
          </InputGroupButtonDropdown>
        </InputGroup>
      </PaginationStyle>
    </div>
  );
}

PaginationBar.propTypes = {
  gotoPage: PropTypes.func,
  previousPage: PropTypes.func,
  nextPage: PropTypes.func,
  canPreviousPage: PropTypes.bool,
  canNextPage: PropTypes.bool,
  pageOptions: PropTypes.arrayOf(PropTypes.number),
  pageIndex: PropTypes.number,
  pageSize: PropTypes.number,
  pageCount: PropTypes.number,
  setPageSize: PropTypes.func,

};
PaginationBar.defaultProps = {
  gotoPage: () => {},
  previousPage: () => {},
  nextPage: () => {},
  canPreviousPage: false,
  canNextPage: true,
  pageOptions: [],
  pageIndex: 1,
  pageSize: 10,
  pageCount: 1,
  setPageSize: () => {},

};

export default PaginationBar;
