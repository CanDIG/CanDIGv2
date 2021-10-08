import React, { useState, useEffect, useRef } from 'react';
import {
  Card, CardBody, CardTitle, Row, Col,
} from 'reactstrap';
import PropTypes from 'prop-types';

import LoadingIndicator, {
  trackPromise,
  usePromiseTracker,
} from '../components/LoadingIndicator/LoadingIndicator';
import CustomOfflineChart from '../components/Graphs/CustomOfflineChart';
import { notify, NotificationAlert } from '../utils/alert';
import { fetchIndividualsFederation } from '../api/api';
import { mergeFederatedResults } from '../utils/utils';
import { schemaFxn } from '../components/Processing/ChordSchemas';

function groupByExtraProperty(data, property) {
  /**
   * Group by some property under extra property
   * from the response data from Chord service
   */
  const obj = {};
  for (let i = 0; i < data.length; i += 1) {
    const key = schemaFxn(() => data[i].extra_properties[property]);
    if (!obj[key]) {
      obj[key] = 0;
    }
    obj[key] += 1;
  }

  return obj;
}

function countFromExtraProperty(data, property) {
  /**
   * Return the count of keys on a object
   */
  return Object.keys(groupByExtraProperty(data, property)).length;
}

function Overview({ updateState }) {
  /**
   * Dashboard landing view
   */
  const [individualsCounter, setIndividualsCounter] = useState(0);
  const [hospitalCounter, setHospitalCounter] = useState(0);
  const [hostHospitalObj, setHostHospitalObj] = useState({ '': 0 });
  const [employmentObj, setEmploymentObj] = useState({ '': 0 });
  const [asymptomaticObj, setAsymptomaticObj] = useState({ '': 0 });
  const [covid19TesteObj, setCovid19TesteObj] = useState({ '': 0 });
  const [hospitalizedObj, setHospitalizedObj] = useState({ '': 0 });
  const [residenceTypeObj, setResidenceTypeObj] = useState({ '': 0 });
  const [hospitalizationRate, setHospitalizationRate] = useState(0);
  const [positiveTestRate, setPositiveTestRate] = useState(0);

  const [didFetch, setDidFetch] = useState(false);

  const { promiseInProgress } = usePromiseTracker();
  const notifyEl = useRef(null);

  useEffect(() => {
    if (!didFetch) {
      trackPromise(
        fetchIndividualsFederation()
          .then((data) => {
            const merged = mergeFederatedResults(data);
            const numberOfIndividuals = merged.length;
            const numberOfHospitalized = groupByExtraProperty(
              merged,
              'hospitalized',
            );
            const numberOfResults = groupByExtraProperty(merged, 'covid19_test');

            setIndividualsCounter(numberOfIndividuals);
            setHospitalizedObj(numberOfHospitalized);
            setCovid19TesteObj(numberOfResults);
            setHospitalizationRate(
              Math.round(
                (numberOfHospitalized.Yes / numberOfIndividuals) * 100,
              ),
            );
            setPositiveTestRate(
              Math.round(
                (numberOfResults.Positive / numberOfIndividuals) * 100,
              ),
            );
            setHospitalCounter(countFromExtraProperty(merged, 'host_hospital'));
            setHostHospitalObj(groupByExtraProperty(merged, 'host_hospital'));
            setEmploymentObj(groupByExtraProperty(merged, 'employment'));
            setAsymptomaticObj(groupByExtraProperty(merged, 'asymptomatic'));
            setResidenceTypeObj(groupByExtraProperty(merged, 'residence_type'));

            setDidFetch(true);
          })
          .catch(() => {
            notify(
              notifyEl,
              'The resources you requested were not available.',
              'warning',
            );
          }),
      );
    }
    updateState({ datasetVisible: false });
    return () => {
      updateState({ datasetVisible: true });
    };
  }, [didFetch, updateState]);

  return (
    <>
      <div className="content">
        <NotificationAlert ref={notifyEl} />
        <Row>
          <Col lg="3" md="12" sm="12">
            <Card className="card-stats">
              <CardBody>
                <Row>
                  <Col md="4" xs="5">
                    <div className="icon-big text-center icon-warning">
                      <i className="nc-icon nc-single-02 text-primary" />
                    </div>
                  </Col>
                  <Col md="8" xs="7">
                    <div className="numbers">
                      <p className="card-category">Individuals</p>
                      {promiseInProgress === true ? (
                        <LoadingIndicator />
                      ) : (
                        <CardTitle tag="p">{individualsCounter}</CardTitle>
                      )}
                      <p />
                    </div>
                  </Col>
                </Row>
              </CardBody>
            </Card>
          </Col>
          <Col lg="3" md="12" sm="12">
            <Card className="card-stats">
              <CardBody>
                <Row>
                  <Col md="4" xs="5">
                    <div className="icon-big text-center icon-warning">
                      <i className="nc-icon nc-bank text-success" />
                    </div>
                  </Col>
                  <Col md="8" xs="7">
                    <div className="numbers">
                      <p className="card-category">Hospitals</p>
                      {promiseInProgress === true ? (
                        <LoadingIndicator />
                      ) : (
                        <CardTitle tag="p">{hospitalCounter}</CardTitle>
                      )}
                      <p />
                    </div>
                  </Col>
                </Row>
              </CardBody>
            </Card>
          </Col>
          <Col lg="3" md="12" sm="12">
            <Card className="card-stats">
              <CardBody>
                <Row>
                  <Col md="4" xs="5">
                    <div className="icon-big text-center icon-warning">
                      <i className="nc-icon nc-ambulance text-warning" />
                    </div>
                  </Col>
                  <Col md="8" xs="7">
                    <div className="numbers">
                      <p className="card-category">Hospitalization Rate</p>
                      {promiseInProgress === true ? (
                        <LoadingIndicator />
                      ) : (
                        <CardTitle tag="p">
                          {hospitalizationRate}
                          %
                        </CardTitle>
                      )}
                      <p />
                    </div>
                  </Col>
                </Row>
              </CardBody>
            </Card>
          </Col>
          <Col lg="3" md="12" sm="12">
            <Card className="card-stats">
              <CardBody>
                <Row>
                  <Col md="4" xs="5">
                    <div className="icon-big text-center icon-warning">
                      <i className="nc-icon nc-simple-add text-danger" />
                    </div>
                  </Col>
                  <Col md="8" xs="7">
                    <div className="numbers">
                      <p className="card-category">Positive Test Rate</p>
                      {promiseInProgress === true ? (
                        <LoadingIndicator />
                      ) : (
                        <CardTitle tag="p">
                          {positiveTestRate}
                          %
                        </CardTitle>
                      )}
                      <p />
                    </div>
                  </Col>
                </Row>
              </CardBody>
            </Card>
          </Col>
        </Row>
        <Row>
          <Col lg="3" md="12" sm="12">
            <Card>
              <CardBody>
                {promiseInProgress === true ? (
                  <LoadingIndicator />
                ) : (
                  <CustomOfflineChart
                    datasetName=""
                    dataObject={residenceTypeObj}
                    chartType="bar"
                    barTitle="Type of residence"
                    height="200px; auto"
                  />
                )}
              </CardBody>
            </Card>
          </Col>
          <Col lg="3" md="12" sm="12">
            <Card>
              <CardBody>
                {promiseInProgress === true ? (
                  <LoadingIndicator />
                ) : (
                  <CustomOfflineChart
                    datasetName=""
                    dataObject={asymptomaticObj}
                    chartType="bar"
                    barTitle="Asymptomatics"
                    height="200px; auto"
                  />
                )}
              </CardBody>
            </Card>
          </Col>
          <Col lg="3" md="12" sm="12">
            <Card>
              <CardBody>
                {promiseInProgress === true ? (
                  <LoadingIndicator />
                ) : (
                  <CustomOfflineChart
                    datasetName=""
                    dataObject={hospitalizedObj}
                    chartType="bar"
                    barTitle="Individuals hospitalized"
                    height="200px; auto"
                  />
                )}
              </CardBody>
            </Card>
          </Col>
          <Col lg="3" md="12" sm="12">
            <Card>
              <CardBody>
                {promiseInProgress === true ? (
                  <LoadingIndicator />
                ) : (
                  <CustomOfflineChart
                    datasetName=""
                    dataObject={covid19TesteObj}
                    chartType="bar"
                    barTitle="Covid19 Test Results"
                    height="200px; auto"
                  />
                )}
              </CardBody>
            </Card>
          </Col>
        </Row>
        <Row>
          <Col lg="6" md="12" sm="12">
            <Card>
              <CardBody>
                {promiseInProgress === true ? (
                  <LoadingIndicator />
                ) : (
                  <CustomOfflineChart
                    datasetName=""
                    dataObject={hostHospitalObj}
                    chartType="pie"
                    barTitle="Host Hospital"
                    height="400px; auto"
                  />
                )}
              </CardBody>
            </Card>
          </Col>
          <Col lg="6" md="12" sm="12">
            <Card>
              <CardBody>
                {promiseInProgress === true ? (
                  <LoadingIndicator />
                ) : (
                  <CustomOfflineChart
                    datasetName=""
                    dataObject={employmentObj}
                    chartType="pie"
                    barTitle="Employment"
                    height="400px; auto"
                  />
                )}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </>
  );
}

Overview.propTypes = {
  updateState: PropTypes.func.isRequired,
};

export default Overview;
