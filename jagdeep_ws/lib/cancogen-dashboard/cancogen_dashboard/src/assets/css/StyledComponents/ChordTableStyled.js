import styled from 'styled-components';

const Styles = styled.div`
  padding: 1rem;
  overflow: auto;

  div.card {
    background: #f4f3ef
    // padding-top: 0px
  }
  table {
    border: 1px solid #127e12;
    background-color: #EEEEEE;
    width: 100%;
    text-align: left;
    border-collapse: collapse;
  }
  table td {
    border-right: 1px solid #127e12;
    padding: 3px 2px;
  }

  table tbody td {
    font-size: 14px;
  }
  table tbody tr:nth-child(even) {
    background: #b0dfb0;
  }
  table thead {
    // background: #1C6EA4;
    // background: -moz-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
    // background: -webkit-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
    // background: linear-gradient(to bottom, #5592bb 0%, #327cad 66%, #1C6EA4 100%);

    background: rgb(23,160,24);
    // background: -moz-linear-gradient(85deg, rgba(23,160,24,1) 10%, rgba(4,117,179,1) 56%, rgba(1,45,100,1) 90%);
    // background: -webkit-linear-gradient(85deg, rgba(23,160,24,1) 10%, rgba(4,117,179,1) 56%, rgba(1,45,100,1) 90%);
    // background: linear-gradient(0deg, rgba(115,197,115,1) 0%, rgba(23,159,23,1) 66%, rgba(18,126,18,1) 100%);
  }
  table thead th {
    font-size: 15px;
    font-weight: bold;
    color: #FFFFFF;
    text-align: center;
    border-left: 1px solid #444444;
  }
  table thead th:first-child {
    border-left: none;
  }

  table tbody tr:hover {
    background-color:#c4d5e7;
  }

  table thead tr th div input {
    margin-right: 3px;
    margin-left: 3px;
    margin-bottom: 2px;
    background-color: #EEEEEE
  }
  
  table tfoot td {
    font-size: 14px;
  }
  table tfoot .links {
    text-align: right;
  }
  table tfoot .links a{
    display: inline-block;
    background: #1C6EA4;
    color: #FFFFFF;
    padding: 2px 8px;
    border-radius: 5px;
  }

`;

export default Styles;
