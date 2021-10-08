import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

import igv from 'igv/dist/igv.esm';
import { NotificationAlert } from '../../utils/alert';
import { HTSGET_URL } from '../../constants/constants';

function HtsgetInstance({ selectedBamName, datasetId }) {
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
          type: 'alignment',
          sourceType: 'htsget',
          name: '',
          url: HTSGET_URL,
          endpoint: '/htsget/v1/reads/',
          id: '',
        },
      ],
    };

    igv.removeAllBrowsers(); // Remove existing browser instances

    // Do not create new browser instance on page load as no sample is selected.
    if (selectedBamName !== '') {
      igvOptions.tracks[0].name = selectedBamName;
      igvOptions.tracks[0].id = selectedBamName;

      igv.createBrowser(igvBrowser.current, igvOptions);
    }
  }, [selectedBamName, datasetId]);

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

HtsgetInstance.propTypes = {
  selectedBamName: PropTypes.string.isRequired,
  datasetId: PropTypes.string.isRequired,
};

export default HtsgetInstance;
