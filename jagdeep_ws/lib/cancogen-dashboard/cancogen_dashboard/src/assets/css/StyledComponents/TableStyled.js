import styled from 'styled-components';

const Styles = styled.div`
  padding: 1rem;
  overflow: auto;

  div.card {
    background: #f4f3ef
  }
  table.mainTable, table.subTable {
    border: 1px solid #579DD9;
    width: 50%;
    text-align: center;
    border-collapse: collapse;
  }
  table.mainTable td, table.subTable td {
    border-right: 1px solid #579DD9;
    padding: 3px 2px;
    max-width: 250px;
    min-width: 100px;

  }

  table.mainTable {
    cursor: pointer;
  }

  table tbody td {
    font-size: 14px;
  }
  table tbody tr:nth-child(even) {
    background: #C7E6F8
  }
  table thead {
    background: #2D6FB3
   
  }
  table.mainTable thead th, table.subTable thead th  {
    font-size: 15px;
    font-weight: bold;
    color: #FFFFFF;
    text-align: center;
    max-width: 200px;
    max-height: 50px;
    padding-left: 5px;
    padding-right: 5px;
  }

  table.mainTable table, table.subTable table {
    margin-right: auto;
    margin-left: auto;
  }

  table.mainTable table th, table.subTable table th {
    cursor: default;
  }

  table.mainTable  th, table.subTable  th {
    cursor: default;
  }

  
  table thead th:first-child {
    border-left: none;
  }

  table tbody tr:hover {
    background-color:#c4d5e7;
  }

  table thead tr th div input, select {
    margin-right: 3px;
    margin-left: 3px;
    margin-bottom: 2px;
    background-color: #FFFFFF;
    width: 100px;
    display: ${(props) => (props.rowFilter ? 'none' : '')};
  }

  th.description {
    min-width: 300px;
  }

  table thead tr th div select {
    max-width: 100px;
    max-height: 50px;
    overflow: auto;
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

  table thead tr th div span[title="Toggle GroupBy"] {
    display: ${(props) => (props.rowAggregation ? 'none' : '')};;
  }


`;

export default Styles;
