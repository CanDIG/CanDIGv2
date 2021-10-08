import styled from 'styled-components';

const Styles = styled.div`
  padding: 1rem;
  overflow: auto;

  table {
    border-spacing: 0;
    border: 1px solid black;

    tr {
      :last-child {
        td {
          border-bottom: 0;
        }
      }
    }

    th,
    td {
      margin: 0;
      padding: 0.5rem;
      border-bottom: 1px solid black;
      border-right: 1px solid black;

      :last-child {
        border-right: 0;
      }
    }


  }



  .pageCountBox {
    margin-left: .3rem;
    // padding: 10px 10px 10px 10px;
  }

  //Need to figure out how to do this for individual inputs

  .form-group .input-group-prepend .input-group-text, 
  .form-group .input-group-append .input-group-text, 
  .input-group .input-group-prepend .input-group-text, 
  .input-group .input-group-append .input-group-text {
    padding: 10px 10px 10px 10px;
  }

  .pageCountOuter {
    background-color: #e9ecef;
  }

  .goToPage {
    background-color: #e9ecef;
  }

  .tablePageInput {
    min-width: 0px;
    width: 10%;
    flex: none
  }

  .input-group .input-group-prepend .btn {
    
    margin-top: 0%;
    margin-bottom: 0%;
    margin-left: 0%;
    margin-right: 0%;
  
  }
`;

export default Styles;
