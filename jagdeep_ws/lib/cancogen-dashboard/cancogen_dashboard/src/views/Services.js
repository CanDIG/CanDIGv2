import React, { useEffect } from 'react';
import PropTypes from 'prop-types';

// reactstrap components
import {
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Table,
  Row,
  Col,
} from 'reactstrap';

import BASE_URL, { CHORD_METADATA_URL, HTSGET_URL, DRS } from '../constants/constants';

function Services({ updateState }) {
  useEffect(() => {
    updateState({ datasetVisible: false });
    return () => {
      updateState({ datasetVisible: true });
    };
  }, [updateState]);
  return (
    <>
      <div className="content">
        <Row>
          <Col md="12">
            <Card>
              <CardHeader>
                <CardTitle tag="h4">Service Status</CardTitle>
              </CardHeader>
              <CardBody>
                <Table responsive>
                  <thead className="text-primary">
                    <tr>
                      <th>Service</th>
                      <th>Service URL</th>
                      <th>Status</th>
                      <th className="text-right">Last Updated</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Candig Server</td>
                      <td>{BASE_URL}</td>
                      <td><i className="nc-icon nc-check-2" /></td>
                      <td className="text-right">Just now</td>
                    </tr>
                    <tr>
                      <td>Katsu Metadata Service</td>
                      <td>{CHORD_METADATA_URL}</td>
                      <td><i className="nc-icon nc-check-2" /></td>
                      <td className="text-right">Just now</td>
                    </tr>
                    <tr>
                      <td>Htsget App</td>
                      <td>{HTSGET_URL}</td>
                      <td><i className="nc-icon nc-check-2" /></td>
                      <td className="text-right">Just now</td>
                    </tr>
                    <tr>
                      <td>DRS Service</td>
                      <td>{DRS}</td>
                      <td><i className="nc-icon nc-check-2" /></td>
                      <td className="text-right">Just now</td>
                    </tr>
                  </tbody>
                </Table>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </>
  );
}

Services.propTypes = {
  updateState: PropTypes.func.isRequired,
};

export default Services;
