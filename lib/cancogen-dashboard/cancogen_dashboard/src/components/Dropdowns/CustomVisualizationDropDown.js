import React, { useState } from 'react';
import PropTypes from 'prop-types';

import {
  Container, Card, CardBody, Row, Col, Input,
} from 'reactstrap';
// Consts
import CustomChart from '../Graphs/CustomChart';
import tableSchema from '../../constants/tableSchema';

/*
 * Visualization component to plot tables and its columns values to different kinds of graphs
 */

function CustomVisualizationDropDown({ datasetId, datasetName }) {
  const [selectedTable, setSelectedTable] = useState('patients');
  const [selectedColumn, setSelectedColumn] = useState('dateOfBirth');
  const [selectedChart, setSelectedChart] = useState('bar');

  /*
   * Transform a camelCase string to a capital spaced string
   */
  function splitString(newString) {
    const splitted = newString.replace(/([a-z])([A-Z])/g, '$1 $2');
    const capitalized = splitted.charAt(0).toUpperCase() + splitted.substr(1);
    return capitalized;
  }

  const tables = Object.keys(tableSchema).map((x) => (
    <option key={x} value={x}>
      {splitString(x)}
    </option>
  ));

  const columns = tableSchema[selectedTable].map((x) => (
    <option key={x} value={x}>
      {splitString(x)}
    </option>
  ));

  const chartList = ['Bar', 'Column', 'Scatter', 'Pie'].map((x) => (
    <option key={x} value={x.toLowerCase()}>
      {x}
    </option>
  ));

  return (
    <>
      <Container fluid>
        <div style={{ marginBottom: '10px' }}>
          <Row>
            <Col xs="6" sm="6" md="4" lg="4" xl="4">
              <Input
                onChange={(e) => {
                  const table = e.currentTarget.value;
                  const column = tableSchema[table][0];
                  setSelectedTable(table);
                  setSelectedColumn(column);
                }}
                type="select"
              >
                {tables}
              </Input>
            </Col>

            <Col xs="6" sm="6" md="4" lg="4" xl="4">
              <Input
                value={selectedColumn}
                onChange={(e) => {
                  setSelectedColumn(e.currentTarget.value);
                }}
                type="select"
              >
                {columns}
              </Input>
            </Col>

            <Col xs="6" sm="6" md="4" lg="4" xl="4">
              <Input
                onChange={(e) => {
                  setSelectedChart(e.currentTarget.value.toLowerCase());
                }}
                type="select"
              >
                {chartList}
              </Input>
            </Col>
          </Row>
        </div>
      </Container>
      <Row>
        <Col>
          <Card>
            <CardBody>
              <CustomChart
                datasetId={datasetId}
                datasetName={datasetName}
                chartType={selectedChart}
                table={selectedTable}
                field={selectedColumn}
              />
            </CardBody>
          </Card>
        </Col>
      </Row>
    </>
  );
}

CustomVisualizationDropDown.propTypes = {
  datasetId: PropTypes.string.isRequired,
  datasetName: PropTypes.string.isRequired,
};

export default CustomVisualizationDropDown;
