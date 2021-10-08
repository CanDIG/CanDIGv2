import React, { useState } from 'react';
import {
  ButtonDropdown, DropdownToggle, DropdownMenu, DropdownItem,
} from 'reactstrap';
import PropTypes from 'prop-types';

// Consts
import { CLIN_METADATA } from '../../constants/constants';

function ClinMetadataDropdown({ metadataCallback, isActive }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState('Type');
  const toggleOpen = () => setIsOpen(!isOpen);

  const handleClick = (entry) => {
    setSelected(entry);

    metadataCallback(entry);
  };

  // TODO: Fix selected update to reflect chosen dataset

  const metadataList = [];
  CLIN_METADATA.forEach((entry) => {
    const capitalized = (entry.charAt(0).toLocaleUpperCase() + entry.slice(1));
    const displayName = [...capitalized.matchAll(/[A-Z]{1}[a-z]*/g)].join(' ');
    metadataList.push(
      <DropdownItem
        onClick={() => handleClick(entry)}
        key={entry}
      >
        {displayName}
      </DropdownItem>,
    );
  });
  if (isActive) {
    return (
      <ButtonDropdown direction="down" isOpen={isOpen} toggle={toggleOpen}>
        <DropdownToggle caret>
          {selected}
        </DropdownToggle>
        <DropdownMenu>
          {metadataList}
        </DropdownMenu>
      </ButtonDropdown>
    );
  }

  return (<></>);
}

ClinMetadataDropdown.propTypes = {
  metadataCallback: PropTypes.func,
  isActive: PropTypes.bool,
};

ClinMetadataDropdown.defaultProps = {
  metadataCallback: () => {},
  isActive: false,
};

export default ClinMetadataDropdown;
