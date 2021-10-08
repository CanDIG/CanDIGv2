// Wrapper function to access nested objects
// returns an empty string if it doesn't exist

export const schemaFxn = (fxn, fallback = '') => {
  try {
    return fxn();
  } catch (error) {
    return fallback;
  }
};

export const diseaseSchema = (data) => {
  const entry = {
    ID: schemaFxn(() => data.id),
    term: schemaFxn(() => data.term.id),
    label: schemaFxn(() => data.term.label),
    comorbidities: schemaFxn(() => data.extra_properties.comorbidities_group),
    created: schemaFxn(() => data.created),
    updated: schemaFxn(() => data.updated),
  };
  return entry;
};

// can be either symptom or complication depending on datatype
export const featureSchema = (data) => {
  const entry = {
    ID: schemaFxn(() => data.type.id),
    label: schemaFxn(() => data.type.label),
    description: schemaFxn(() => data.description),
    negated: schemaFxn(() => data.negated),
    created: schemaFxn(() => data.created),
    updated: schemaFxn(() => data.updated),
  };
  return entry;
};

export const subjectSchema = (data) => {
  const subject = {
    ID: schemaFxn(() => data.id),
    DOB: schemaFxn(() => data.date_of_birth),
    Sex: schemaFxn(() => data.sex),
    KSex: schemaFxn(() => data.karyotypic_sex),
    ethnicity: schemaFxn(() => data.ethnicity),
    height: schemaFxn(() => data.extra_properties.height),
    weight: schemaFxn(() => data.extra_properties.weight),
    education: schemaFxn(() => data.extra_properties.education),
    abo_type: schemaFxn(() => data.extra_properties.abo_type),
    taxID: schemaFxn(() => data.taxonomy.id),
    taxLabel: schemaFxn(() => data.taxonomy.label),
    household: schemaFxn(() => data.extra_properties.household),
    employment: schemaFxn(() => data.extra_properties.employment),
    asymptomatic: schemaFxn(() => data.extra_properties.asymptomatic),
    covid19_test: schemaFxn(() => data.extra_properties.covid19_test),
    covid19_test_date: schemaFxn(() => data.extra_properties.covid19_test_date),
    covid19_diagnosis_date: schemaFxn(() => data.extra_properties.covid19_diagnosis_date),
    hospitalized: schemaFxn(() => data.extra_properties.hospitalized),
    birth_country: schemaFxn(() => data.extra_properties.birth_country),
    host_hospital: schemaFxn(() => data.extra_properties.host_hospital),
    residence_type: schemaFxn(() => data.extra_properties.residence_type),
    enrollment_date: schemaFxn(() => data.extra_properties.enrollment_date),
    created: schemaFxn(() => data.created),
    updated: schemaFxn(() => data.updated),
  };
  return subject;
};

// Called when using /api/individuals

export function ProcessMetadata(metadata) {
  const mainTable = [];
  const phenopacketsList = {};
  Object.values(metadata).forEach((entry) => {
    mainTable.push(subjectSchema(entry));
    const ID = entry.id;
    let Pheno;
    /* eslint-disable */
    try {
      Pheno = entry.phenopackets[0];
      phenopacketsList[ID] = Pheno;
    } catch (e) {}
    /* eslint-enable */
  });
  return [mainTable, phenopacketsList];
}

// Called when using /api/phenopackets

export function ProcessPhenopackets(response) {
  // console.log(response);
  const mainTable = [];
  const phenopacketsList = {};
  response.forEach((entry) => {
    // console.log(entry);
    mainTable.push(subjectSchema(entry.subject));
    const ID = entry.id;
    phenopacketsList[ID] = entry;
  });

  return [mainTable, phenopacketsList];
}

export function ProcessData(ID, dataList, dataSchema) {
  const processedData = [];
  Object.values(dataList).forEach((data) => {
    const dataEntry = dataSchema(data);
    processedData.push(dataEntry);
  });
  return { [ID]: processedData };
}

export function ProcessFeatures(ID, dataList, dataSchema, feature) {
  const processedFeatures = [];

  Object.values(dataList)
    .filter((data) => data.extra_properties.datatype === feature)
    .forEach((entry) => {
      const dataEntry = dataSchema(entry);
      processedFeatures.push(dataEntry);
    });

  // console.log(processedFeatures);
  return { [ID]: processedFeatures };
}

export async function ProcessSymptoms(phenopackets) {
  const symptoms = new Set();
  Promise.all(Object.values(phenopackets).map(async (phenopacket) => {
    await Promise.all(phenopacket.phenotypic_features.map(async (feature) => {
      if (feature.extra_properties.datatype === 'symptom') {
        symptoms.add(feature.type.label);
      }
    }));
  }));

  const symptomList = Array.from(symptoms).map((symptom) => ({ name: symptom }));

  return symptomList;
}
