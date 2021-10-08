import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
// Custom CSS
import '../assets/css/APIInfo.css';

// reactstrap components
import {
  Card, CardBody, Row, Col, Table, Input,
} from 'reactstrap';

// Consts
import BASE_URL from '../constants/constants';

/*
 * API Info component
 */
function APIInfo({ updateState }) {
  const [apiDef, setApiDef] = useState(`${BASE_URL}/static/api.yaml`);
  const apiDefinitionObj = {
    'CanDIG-Server V1 API': `${BASE_URL}/static/api.yaml`,
    'CanDIG-Server V1 Search & Count API': `${BASE_URL}/static/search_count_service.yaml`,
    'CHORD Metadata Service': `${BASE_URL}/static/chord_metadata_service.yaml`,
  };
  const apiList = Object.keys(apiDefinitionObj).map((x) => (
    <option key={x} value={x}>
      {x}
    </option>
  ));

  useEffect(() => {
    updateState({ datasetVisible: false });
    return () => {
      updateState({ datasetVisible: true });
    };
  }, [updateState]);

  return (
    <>
      <div className="content">

        <Input
          onChange={(e) => {
            setApiDef(apiDefinitionObj[e.currentTarget.value]);
          }}
          type="select"
        >
          { apiList }
        </Input>

        <Row>
          <Col md="12">
            <Card>
              <CardBody className="all-icons">
                <Table responsive>
                  <SwaggerUI url={apiDef} />
                </Table>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </>
  );
}

APIInfo.propTypes = {
  updateState: PropTypes.func.isRequired,
};

export default APIInfo;
