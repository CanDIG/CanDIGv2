import React, {
  useState, useRef,
} from 'react';
import PropTypes from 'prop-types';

import {
  Button, InputGroup,
  InputGroupAddon, Col, Input,
} from 'reactstrap';
import Autosuggest from 'react-autosuggest';
import AutoSuggestStyle from '../../assets/css/StyledComponents/AutoSuggestStyled';
import Style from '../../assets/css/StyledComponents/ColumnControlStyled';
import { NotificationAlert } from '../../utils/alert';

function SearchBySymptom({
  setSymptom, fetchData, fetchedSuggestions,
}) {
  const [search, setSearch] = useState('');
  const [value, setValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const notifyEl = useRef(null);

  // From https://github.com/moroshko/react-autosuggest#installation

  const getSuggestions = (input) => {
    const inputValue = input.trim().toLowerCase();
    const inputLength = inputValue.length;
    return inputLength === 0 ? [] : fetchedSuggestions.filter((lang) => lang.name.toLowerCase().slice(0, inputLength) === inputValue);
  };

  const getSuggestionValue = (suggestion) => suggestion.name;

  const renderSuggestion = (suggestion) => (
    <div>
      {suggestion.name}
    </div>
  );

  // 3rd Party implmentation, disabling the linter because it doesn't like the value shadowing
/* eslint-disable */

  const onSuggestionsFetchRequested = ({ value }) => {
    setSuggestions(getSuggestions(value));
  };
  /* eslint-enable */

  // Autosuggest will call this function every time you need to clear suggestions.
  const onSuggestionsClearRequested = () => {
    setSuggestions([]);
  };

  const onChange = (event, { newValue }) => {
    setValue(newValue);
    setSearch(newValue);
  };

  const inputProps = {
    placeholder: 'Symptom...',
    value,
    onChange,
  };

  const renderInputComponent = (iProps) => (
    <div>
      <InputGroup>
        <Input {...iProps} />
        <InputGroupAddon addonType="append">
          <Button onClick={() => setSymptom(search)}>Search</Button>

        </InputGroupAddon>
      </InputGroup>
    </div>
  );

  return (
    <>
      <Style>
        <NotificationAlert ref={notifyEl} />

        <Col xs="4">
          <Button onClick={fetchData}> All Data</Button>
        </Col>
        <Col xs="4">

          <AutoSuggestStyle>
            <Autosuggest
              suggestions={suggestions}
              onSuggestionsFetchRequested={onSuggestionsFetchRequested}
              onSuggestionsClearRequested={onSuggestionsClearRequested}
              getSuggestionValue={getSuggestionValue}
              renderSuggestion={renderSuggestion}
              renderInputComponent={renderInputComponent}
              inputProps={inputProps}
            />
          </AutoSuggestStyle>

        </Col>
        <Col xs="4" />

      </Style>

    </>
  );
}

SearchBySymptom.propTypes = {
  setSymptom: PropTypes.func,
  fetchData: PropTypes.func,
  fetchedSuggestions: PropTypes.arrayOf(PropTypes.object),
};

SearchBySymptom.defaultProps = {
  setSymptom: () => {},
  fetchData: () => {},
  fetchedSuggestions: [],
};

export default SearchBySymptom;
