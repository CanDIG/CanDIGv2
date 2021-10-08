import React, { useState, useEffect, useRef } from 'react';
import { Row, Input, UncontrolledAlert } from 'reactstrap';
import VcfInstance from '../components/IGV/VcfInstance';
import { notify, NotificationAlert } from '../utils/alert';

// Consts
import { DRS } from '../constants/constants';

function VcfBrowser() {
  /** *
   * A functional component that renders a view with a IGV.js browser.
   */
  const [selectedVcfName, setSelectedVcfName] = useState('');
  const [selectedVcfLink, setSelectedVcfLink] = useState('');
  const [selectedVcfIndexLink, setSelectedVcfIndexLink] = useState('');
  const [vcfDropdown, setVcfDropdown] = useState([]);
  const [vcfDataObj, setVcfDataObj] = useState({});
  const notifyEl = useRef(null);

  const disabledElementList = [
    <option key="disabled" value="disabled" disabled>
      Select a VCF Sample...
    </option>,
  ];

  useEffect(() => {
    fetch(`${DRS}/search?fuzzy_name=.vcf`)
      .then((response) => response.json())
      .then((data) => {
        const tmpDataObj = {};

        // File name is set as key, while its url is set as the value
        data.forEach((element) => {
          if (element.name.endsWith('vcf.gz')) {
            if (!(element.name in tmpDataObj)) {
              tmpDataObj[element.name] = {};
              tmpDataObj[element.name].vcf_file_link = element.access_methods[1].access_url.url.replace('s3://', 'http://');
            } else {
              tmpDataObj[element.name].vcf_file_link = element.access_methods[1].access_url.url.replace('s3://', 'http://');
            }
          }

          if (element.name.endsWith('vcf.gz.tbi')) {
            const fileName = element.name.replace('.tbi', '');

            if (!(fileName in tmpDataObj)) {
              tmpDataObj[fileName] = {};
              tmpDataObj[fileName].vcf_index_link = element.access_methods[1].access_url.url.replace('s3://', 'http://');
            } else {
              tmpDataObj[fileName].vcf_index_link = element.access_methods[1].access_url.url.replace('s3://', 'http://');
            }
          }
        });

        const vcfList = Object.keys(tmpDataObj).map((x) => (
          <option key={x} value={x}>
            {x}
          </option>
        ));

        setVcfDataObj(tmpDataObj);
        setVcfDropdown(vcfList);
      })
      .catch(() => {
        notify(
          notifyEl,
          'No VCF Samples are available.',
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
                <p> Select a sample to get started.</p>
              </span>
            </b>
          </UncontrolledAlert>
        </Row>

        <Input
          defaultValue="disabled"
          onChange={(e) => {
            setSelectedVcfName(e.currentTarget.value);
            setSelectedVcfLink(vcfDataObj[e.currentTarget.value].vcf_file_link);
            setSelectedVcfIndexLink(vcfDataObj[e.currentTarget.value].vcf_index_link);
          }}
          type="select"
        >
          { disabledElementList.concat(vcfDropdown) }
        </Input>

        <VcfInstance
          selectedVcfName={selectedVcfName}
          selectedVcfLink={selectedVcfLink}
          selectedVcfIndexLink={selectedVcfIndexLink}
        />
      </div>
    </>
  );
}

export default VcfBrowser;
