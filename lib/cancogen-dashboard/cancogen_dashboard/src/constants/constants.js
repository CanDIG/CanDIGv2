/*
 * All the constants should go on this file
 */

// API URL where the Dashboard get all the data
const BASE_URL = process.env.REACT_APP_BASE_URL;

export const CHORD_METADATA_URL = process.env.REACT_APP_METADATA_URL;
export const DRS = process.env.REACT_APP_DRS_URL;
export const FEDERATION_URL = process.env.REACT_APP_FEDERATION_URL;
export const HTSGET_URL = process.env.REACT_APP_HTSGET_URL;
export const LOCATION = process.env.REACT_APP_LOCATION;
export const CLIN_METADATA = [
  'celltransplants',
  'chemotherapies',
  'complications',
  'consents',
  'diagnoses',
  'enrollments',
  'immunotherapies',
  'labtests',
  'outcomes',
  'patients',
  'radiotherapies',
  'samples',
  'slides',
  'studies',
  'surgeries',
  'treatments',
  'tumourboards',
];

export default BASE_URL;
