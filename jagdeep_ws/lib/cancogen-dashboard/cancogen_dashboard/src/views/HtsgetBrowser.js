import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { Row, Input, UncontrolledAlert } from 'reactstrap';
import HtsgetInstance from '../components/IGV/HtsgetInstance';
import { notify, NotificationAlert } from '../utils/alert';

// Consts
import { DRS } from '../constants/constants';

function HtsgetBrowser({ datasetId }) {
  /** *
   * A functional component that renders a view with a IGV.js browser.
   */
  const [selectedBamName, setSelectedBamName] = useState('');
  const [bamDropdown, setBamDropdown] = useState([]);
  const notifyEl = useRef(null);

  const disabledElementList = [
    <option key="disabled" value="disabled" disabled>
      Select a BAM Sample...
    </option>,
  ];

  useEffect(() => {
    fetch(`${DRS}/search?fuzzy_name=.bam`)
      .then((response) => response.json())
      .then((data) => {
        const tmpDataObj = {};
        // File name is set as key, while its url is set as the value
        data.forEach((element) => {
          if (!element.name.endsWith('bai')) {
            tmpDataObj[element.name] = element.access_methods[0].access_url.url;
          }
        });

        const bamList = Object.keys(tmpDataObj).map((x) => (
          <option key={x} value={x}>
            {x}
          </option>
        ));

        setBamDropdown(bamList);
      })
      .catch(() => {
        notify(
          notifyEl,
          'No BAM Samples are available.',
          'warning',
        );
      });
  }, []);

  return (
    <>
      <div className="content">
        <NotificationAlert ref={notifyEl} />
        <Row>
          <UncontrolledAlert color="info" className="ml-auto mr-auto alert-with-icon" fade={false}>
            <span
              data-notify="icon"
              className="nc-icon nc-bell-55"
            />

            <b>
              <span>
                <p> Reminders: </p>
                <p> Select a sample to get started. Only .bam files are supported for now.</p>
              </span>
            </b>
          </UncontrolledAlert>
        </Row>

        <Input
          defaultValue="disabled"
          onChange={(e) => {
            setSelectedBamName(e.currentTarget.value);
          }}
          type="select"
        >
          { disabledElementList.concat(bamDropdown) }
        </Input>

        <HtsgetInstance
          selectedBamName={selectedBamName}
          datasetId={datasetId}
        />
      </div>
    </>
  );
}

HtsgetBrowser.propTypes = {
  datasetId: PropTypes.string.isRequired,
};

export default HtsgetBrowser;
