import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

import igv from 'igv/dist/igv.esm';
import { NotificationAlert } from '../../utils/alert';

function VcfInstance({ selectedVcfName, selectedVcfLink, selectedVcfIndexLink }) {
  /** *
   * A functional component that returns an IGV.js instance dedicated to rendering GWAS data.
   */
  const igvBrowser = useRef(null);
  const notifyEl = useRef(null);

  useEffect(() => {
    const igvOptions = {
      genome: 'hg38',
      tracks: [
        {
          type: 'variant',
          format: 'vcf',
          url: '',
          indexURL: '',
          name: '',
          squishedCallHeight: 1,
          expandedCallHeight: 4,
          displayMode: 'squished',
          height: 250,
          visibilityWindow: 10000,
        },
      ],
    };

    igv.removeAllBrowsers(); // Remove existing browser instances

    // Do not create new browser instance on page load as no sample is selected.
    if (selectedVcfName !== '') {
      igvOptions.tracks[0].name = selectedVcfName;
      igvOptions.tracks[0].url = selectedVcfLink;
      igvOptions.tracks[0].indexURL = selectedVcfIndexLink;

      igv.createBrowser(igvBrowser.current, igvOptions);
    }
  }, [selectedVcfName, selectedVcfLink, selectedVcfIndexLink]);

  return (
    <>
      <NotificationAlert ref={notifyEl} />

      <div
        style={{ background: 'white', marginTop: '15px', marginBottom: '15px' }}
        ref={igvBrowser}
      />
    </>
  );
}

VcfInstance.propTypes = {
  selectedVcfName: PropTypes.string.isRequired,
  selectedVcfLink: PropTypes.string.isRequired,
  selectedVcfIndexLink: PropTypes.string.isRequired,
};

export default VcfInstance;
