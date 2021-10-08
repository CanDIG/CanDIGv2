import styled from 'styled-components';
import { InputGroup } from 'reactstrap';

const Style = styled(InputGroup)`
  min-width: 0px;
  // width: 10%;
  // flex: none

  button {
    margin-top: 0%;
    margin-bottom: 0%;
    // background-color: #0b65a3;
    background: #2D6FB3

  }

  button.dropdown-item {
    background: #FFFFFF
  }

  button.dropdown-item.active {
    background: #EEEEEE
  }

  .dropdown-menu {
    max-height: 400px;
    overflow: auto;
  }

  button:hover {
    background-color: #17a018
  }

  .globalSearchText {
    background-color: #CBF2FA;
  }

  input.globalFilter.form-control {
    background-color: #EEEEEE
  }

  // Not sure why .globalSearchBar doesn't work here
  .input-group .input-group-prepend .input-group-text {
    padding: 10px 10px 10px 10px;
  }
`;

export default Style;
