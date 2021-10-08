import styled from 'styled-components';
import { InputGroup } from 'reactstrap';

const Styles = styled(InputGroup)`
  .pageCountBox {
    margin-left: .3rem;
  }

  //Need to figure out how to do this for individual inputs

  .form-group .input-group-prepend .input-group-text, 
  .form-group .input-group-append .input-group-text, 
  .input-group .input-group-prepend .input-group-text, 
  .input-group .input-group-append .input-group-text {
    padding: 10px 10px 10px 10px;
  }

  .pageCountOuter, .goToPage {
    background-color: #CBF2FA;
  }

  button.btn.btn-secondary.disabled {
    background-color: #355D78
  }

  button.btn.btn-secondary {
    background-color: #0b65a3
  }

  .tablePageInput.form-control {
    min-width: 0px;
    width: 10%;
    flex: none;
    background-color: #EEEEEE
  }



  .input-group .input-group-prepend .btn {
    
    margin-top: 0%;
    margin-bottom: 0%;
    margin-left: 0%;
    margin-right: 0%;
  
  }
`;

export default Styles;
