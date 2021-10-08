"""
HDF5 Query tool
"""
import h5py
import numpy as np
import flask
import pandas as pd
from collections import OrderedDict
from operator import le, ge

app = flask.current_app
SUPPORTED_OUTPUT_FORMATS = ["json", "h5", "loom"]


class UnsupportedOutputError(ValueError):
    """
    Custom exception for passing unsupported file outputs
    """
    def __init__(self):
        message = "Valid output formats are: {}".format(SUPPORTED_OUTPUT_FORMATS)
        super().__init__(message)


class ExpressionQueryTool(object):
    """
    Supports searching expression data from properly formatted HDF5 files
        - sample id
        - features by list:
            - feature accession
            - feature name
            - feature id
        - expression threshold array:
            - either minThreshold or maxThreshold
            - feature type given by featureThresholdLabel: id or name
            - [(feature1, threshold1), (feature2, theshold2)...]
    """

    def __init__(self, input_file, output_file=None, include_metadata=False, output_type="h5", feature_map=None):
        """

        :param input_file: path to HDF5 file being queried
        :param output_file: path where output file should be generated (for non JSON output types)
        :param include_metadata: (bool) include expression file metadata in results
        :param output_type: json | h5 (loom in progress)
        :param feature_map: tsv file containing mapping for gene_id<->gene_name<->accessions
        """
        self._file = h5py.File(input_file, 'r')
        self._output_file = output_file
        self._feature_map = feature_map
        self._expression_matrix = "expression"
        self._features = "axis/features"
        self._samples = "axis/samples"
        self._counts = "metadata/counts"
        # TODO: metadata inclusion needs testing
        self._include_metadata = include_metadata

        if output_type not in SUPPORTED_OUTPUT_FORMATS:
            raise UnsupportedOutputError()
        else:
            self._output_format = output_type

    def get_features(self):
        """
        :return HDF5 features array data set
        """
        return self._file[self._features]

    def get_samples(self):
        """
        :return HDF5 samples array data set
        """
        return self._file[self._samples]

    def get_expression_matrix(self):
        """
        :return HDF5 expression matrix data set
        """
        return self._file[self._expression_matrix]

    def get_raw_counts(self):
        """
        :return HDF5 raw counts metadata set
        """
        return self._file[self._counts]

    def _get_hdf5_indices(self, axis, id_list):
        """

        :param axis: axis data set from hdf5 file
        :param id_list: list of id's to convert into indices
        :return: an ordered dict of id,index pairs (from index low->high)
        """
        indices = {}
        encoded_list = list(map(str.encode, id_list))
        arr = self._file[axis][:]
        for encoded_id in encoded_list:
            lookup = np.where(arr == encoded_id)[0]
            if len(lookup) > 0:
                indices[encoded_id.decode()] = lookup[0]
        sorted_indices = sorted(indices.items(), key=lambda i: i[1])
        if not sorted_indices:
            raise LookupError("Indices for {} could not be generated".format(axis))
        return OrderedDict([(k, v) for (k, v) in sorted_indices])

    def _search_samples(self, sample_list):
        expression = self.get_expression_matrix()
        indices = self._get_hdf5_indices(self._samples, sample_list)

        results = self._build_results_template(expression)

        sample_expressions = list(expression[indices.values(), ...])
        feature_load = self.get_features()[...]

        if self._output_format == "json":
            results["features"] = ExpressionQueryTool.decode_h5_array(feature_load)
            results["expression"] = dict(zip(indices.keys(), map(list, sample_expressions)))

        elif self._output_format == "h5":
            encoded_samples = [sample_id.encode('utf8') for sample_id in indices]

            results = self._write_hdf5_results(
                results, encoded_samples, feature_load, sample_expressions)

            results[self._expression_matrix].attrs["units"] = expression.attrs.get("units")

        elif self._output_format == "loom":
            feature_decode = ExpressionQueryTool.decode_h5_array(feature_load)
            results["ra"]["GeneID"] = np.array(feature_decode)
            results["ra"]["GeneName"] = np.array(self.accession_to_gene(feature_decode))
            results["matrix"] = np.transpose(sample_expressions)
            results["ca"]["Sample"] = np.array(list(indices.keys()))

            # TODO: use real values
            results["ca"]["Condition"] = np.zeros(len(indices))
            results["ca"]["Tissue"] = np.zeros(len(indices))

        return results

    def _search_features(self, feature_list, min_ft=None, max_ft=None,
                         supplementary_feature_label=None, sample_filter=None):
        """
        feature_list must be a list of gene ID valid to data set
        """
        expression = self.get_expression_matrix()
        samples = self.get_samples()
        indices = self._get_hdf5_indices(self._features, feature_list)
        results = self._build_results_template(expression)
        supplementary_feature_array = None

        if supplementary_feature_label:
            supplementary_feature_array = []
            for feature_id in indices:
                supplementary_feature_array.append(supplementary_feature_label[feature_id])

        feature_slices = list(indices.values())

        if min_ft or max_ft:
            if self._output_format == "json":
                if supplementary_feature_array:
                    results["features"] = ExpressionQueryTool.decode_h5_array(supplementary_feature_array)
                else:
                    results["features"] = list(feature_list)

            # read slices in to memory as a data frame
            expression_df = pd.DataFrame(expression[:, feature_slices])
            if sample_filter:
                sample_indices = self._get_hdf5_indices(self._samples, sample_filter)
                sample_filter_indices = [sample_indices[x] for x in sample_indices]
                expression_df = expression_df.iloc[sample_filter_indices, :]

            index_keys = list(indices.keys())

            if min_ft:
                expression_df = self.apply_threshold(expression_df, min_ft, index_keys, ge)

            if max_ft:
                expression_df = self.apply_threshold(expression_df, max_ft, index_keys, le)

            search_expressions = expression_df.values
            samples_list = [samples[idx].decode() for idx in expression_df.index]
            if not samples_list:
                raise LookupError("No threshold matches found")

        else:
            if self._output_format == "json":
                if supplementary_feature_array:
                    results["features"] = ExpressionQueryTool.decode_h5_array(supplementary_feature_array)
                else:
                    results["features"] = list(indices.keys())

            search_expressions = list(expression[:, feature_slices])
            samples_list = ExpressionQueryTool.decode_h5_array(self.get_samples())

        if self._output_format == "json":
            results["expression"] = dict(zip(samples_list, (map(list, search_expressions))))

        elif self._output_format == "h5":
            encoded_samples = [sample.encode('utf-8') for sample in samples_list]
            encoded_features = [feature.encode('utf-8') for feature in indices]

            results = self._write_hdf5_results(
                results, encoded_samples, encoded_features, search_expressions,
                suppl_features_label=supplementary_feature_array)

        elif self._output_format == "loom":
            results["matrix"] = np.array(np.transpose(search_expressions))
            feature_decode = [feature for feature in indices]
            results["ra"]["GeneID"] = np.array(feature_decode)
            results["ra"]["GeneName"] = np.array(self.accession_to_gene(feature_decode))
            results["ca"]["Sample"] = np.array(samples_list)

            # TODO: use real values
            results["ca"]["Condition"] = np.zeros(len(samples_list))
            results["ca"]["Tissue"] = np.zeros(len(samples_list))

        return results

    def search(self, samples=None, feature_id_list=None, feature_accession_list=None, feature_name_list=None):
        """
        General search function. Accepts any combination of the following arguments:
        - sample_id || feature_list_id or feature_list_accession or feature_list_name || sample_id and feature_list
        """
        supplementary_feature_label = {}

        if feature_accession_list or feature_name_list:
            if feature_id_list or (feature_accession_list and feature_name_list):
                raise LookupError("Can't lookup invalid combination of features")
            df = pd.read_csv(self._feature_map, sep='\t')
            feature_id_list = []

            if feature_name_list:
                df_key = 'gene_symbol'
                feature_list = feature_name_list
            else:
                df_key = 'accession_numbers'
                feature_list = feature_accession_list

            for feature_value in feature_list:
                df_lookup = df.loc[df[df_key] == feature_value].ensembl_id
                if len(df_lookup) > 0:
                    gene_id = df_lookup.values[0]
                    feature_id_list.append(gene_id)
                    supplementary_feature_label[gene_id] = feature_value

            for sf in supplementary_feature_label:
                supplementary_feature_label[sf] = supplementary_feature_label[sf].encode('utf-8')

        if samples and feature_id_list:
            expression = self.get_expression_matrix()
            sample_indices = self._get_hdf5_indices(self._samples, samples)
            feature_indices = self._get_hdf5_indices(self._features, feature_id_list)
            results = self._build_results_template(expression)
            supplementary_feature_array = None

            if supplementary_feature_label:
                supplementary_feature_array = []
                for feature_id in feature_indices:
                    supplementary_feature_array.append(supplementary_feature_label[feature_id])

            feature_expressions = []
            feature_slices = feature_indices.values()
            for sample_index in sample_indices.values():
                feature_expressions.append(expression[sample_index, feature_slices])

            if self._output_format == "json":
                if supplementary_feature_array:
                    results["features"] = ExpressionQueryTool.decode_h5_array(supplementary_feature_array)
                else:
                    results["features"] = list(feature_indices.keys())
                results["expression"] = dict(zip(sample_indices.keys(), map(list, feature_expressions)))

            elif self._output_format == "h5":
                encoded_samples = [sample_id.encode('utf8') for sample_id in sample_indices]
                encoded_features = [feature.encode('utf-8') for feature in feature_indices]

                results = self._write_hdf5_results(
                    results, encoded_samples, encoded_features, feature_expressions,
                    suppl_features_label=supplementary_feature_array)

            elif self._output_format == "loom":
                results["matrix"] = np.transpose(feature_expressions)
                feature_decode = [feature for feature in feature_indices]
                results["ra"]["GeneID"] = np.array(feature_decode)
                results["ra"]["GeneName"] = np.array(self.accession_to_gene(feature_decode))
                results["ca"]["Sample"] = np.array(list(sample_indices.keys()))

                # TODO: use real values
                results["ca"]["Condition"] = np.zeros(len(sample_indices))
                results["ca"]["Tissue"] = np.zeros(len(sample_indices))

            return results

        elif samples:
            return self._search_samples(samples)

        elif feature_id_list:
            return self._search_features(feature_id_list, supplementary_feature_label=supplementary_feature_label)

        else:
            raise LookupError("No valid features or samples provided")

    def search_threshold(self, min_ft=None, max_ft=None, feature_id_list=None,
                         feature_name_list=None, samples=None):

        if not max_ft and not min_ft:
            raise ValueError("At least one threshold array is required")

        supplementary_feature_label = {}
        df = pd.read_csv(self._feature_map, sep='\t')
        min_threshold_array_id = None
        min_feature_list = []
        max_threshold_array_id = None
        max_feature_list = []

        if min_ft:
            min_threshold_array = ExpressionQueryTool.convert_threshold_array(min_ft)
            if ExpressionQueryTool.validate_threshold_object(min_ft[0])[0] == 'featureName':
                min_threshold_array_id = []

                for feature, threshold in min_threshold_array:
                    df_lookup = df.loc[df['gene_symbol'] == feature].ensembl_id
                    if len(df_lookup) > 0:
                        gene_id = df_lookup.values[0]
                        min_threshold_array_id.append((gene_id, threshold))
                        if not feature_id_list and not feature_name_list:
                            min_feature_list.append(gene_id)
                            supplementary_feature_label[gene_id] = feature
            else:
                min_feature_list = list(zip(*min_threshold_array))[0]
                min_threshold_array_id = min_threshold_array

        if max_ft:
            max_threshold_array = ExpressionQueryTool.convert_threshold_array(max_ft)
            if ExpressionQueryTool.validate_threshold_object(max_ft[0])[0] == 'featureName':
                max_threshold_array_id = []

                for feature, threshold in max_threshold_array:
                    df_lookup = df.loc[df['gene_symbol'] == feature].ensembl_id
                    if len(df_lookup) > 0:
                        gene_id = df_lookup.values[0]
                        max_threshold_array_id.append((gene_id, threshold))
                        if not feature_id_list and not feature_name_list:
                            max_feature_list.append(gene_id)
                            supplementary_feature_label[gene_id] = feature
            else:
                max_feature_list = list(zip(*max_threshold_array))[0]
                max_threshold_array_id = max_threshold_array

        if feature_name_list:
            feature_list_parsed = self.gene_to_accession(feature_name_list)
            supplementary_feature_label = dict(zip(feature_list_parsed, feature_name_list))
        elif feature_id_list:
            feature_list_parsed = feature_id_list
        else:
            feature_list_parsed = []

        if not feature_list_parsed:
            if max_ft and min_ft:
                feature_list_parsed = list(set(min_feature_list) | set(max_feature_list))
            elif min_ft:
                feature_list_parsed = min_feature_list
            else:
                feature_list_parsed = max_feature_list

        for sf in supplementary_feature_label:
            supplementary_feature_label[sf] = supplementary_feature_label[sf].encode('utf-8')

        return self._search_features(
            feature_list_parsed, min_ft=min_threshold_array_id, max_ft=max_threshold_array_id,
            supplementary_feature_label=supplementary_feature_label, sample_filter=samples
        )

    def _write_hdf5_results(self, results, sample_list, feature_list, expressions,
                            suppl_features_label=None, transpose=False):
        features_ds = results.create_dataset(
            self._features, (len(feature_list), 1), maxshape=(len(feature_list), 2), dtype="S20")
        features_data = [feature_list]

        if suppl_features_label:
            features_ds.resize((len(feature_list), 2))
            features_data.append(suppl_features_label)

        features_ds[...] = np.transpose(features_data)

        samples_ds = results.create_dataset(
            self._samples, (len(sample_list),), maxshape=(len(sample_list),), dtype="S40")
        samples_ds[...] = sample_list

        expression_ds = results.create_dataset(
            self._expression_matrix, (len(sample_list), len(feature_list)),
            maxshape=(len(sample_list), len(feature_list)), chunks=True, dtype="f8")

        ref_ds = self.get_expression_matrix()
        expression_ds.attrs["units"] = ref_ds.attrs.get("units")
        expression_ds.attrs["study"] = ref_ds.attrs.get("study")

        if transpose:
            expression_ds[...] = np.transpose(expressions)
        else:
            expression_ds[...] = expressions

        return results

    def _write_hdf5_metadata(self, results, num_samples, num_features, counts=None):
        """
        Write metadata matrices to file
        :param results: the results file-object being written to
        :return:
        """
        if counts is not None:
            counts_ds = results.create_dataset(
                self._counts, (num_samples, num_features),
                maxshape=(num_samples, num_features), chunks=True, dtype="f8")

            counts_ds[...] = counts

        return results

    def _build_results_template(self, expression_matrix):
        """
        Construct a results object template from the expression dataset
        """
        if self._output_format == 'json':
            results = {
                "expression": {},
                "features": [],
                "units": expression_matrix.attrs.get("units"),
                "study": expression_matrix.attrs.get("study")
            }

            if self._include_metadata:
                # TODO: default metadata fields? so far units only required
                results["metadata"] = {
                    "units": expression_matrix.attrs.get("units"),
                    "raw_counts": {}
                }

        elif self._output_format == 'h5':
            results = h5py.File(self._output_file, 'w', driver='core')

        elif self._output_format == 'loom':
            # make a dict to pass to loompy.create()
            results = {
                'filename': self._output_file,
                'matrix': None,
                'ra': {},
                'ca': {},
                'units': expression_matrix.attrs.get("units")
            }
        else:
            results = None

        return results

    def accession_to_gene(self, feature_list):
        df = pd.read_csv(self._feature_map, sep='\t')
        gene_list = []
        for feature_id in feature_list:
            df_lookup = df.loc[df['ensembl_id'] == feature_id].gene_symbol
            if len(df_lookup) > 0:
                gene_name = df_lookup.values[0]
                gene_list.append(gene_name)
            else:
                gene_list.append(feature_id)
        return gene_list

    def gene_to_accession(self, feature_list):
        df = pd.read_csv(self._feature_map, sep='\t')
        id_list = []
        for gene_name in feature_list:
            df_lookup = df.loc[df['gene_symbol'] == gene_name].ensembl_id
            if len(df_lookup) > 0:
                accession_id = df_lookup.values[0]
                id_list.append(accession_id)
            else:
                id_list.append(gene_name)
        return id_list

    def close(self):
        self._file.close()

    @staticmethod
    def apply_threshold(df, thresholds, idx_keys, cmp):
        """

        :param df: pandas data frame to filter
        :param thresholds: tuple of thresholds to apply
        :param idx_keys: feature index mapping
        :param cmp: comparison function to apply
        :return: filtered data frame
        """
        for feature_id, threshold in thresholds:
            # slice data frame while samples remain
            if len(df) > 0:
                try:
                    df_feature_index = idx_keys.index(feature_id)
                    df = df[cmp(df[df_feature_index], threshold)]
                except ValueError:
                    continue
            else:
                break
        return df

    @staticmethod
    def convert_threshold_array(threshold_input):
        """
        query parameter threshold array formatted: Feature,Value,Feature,Value
        :param threshold_input: threshold object array
        :return: list of feature/threshold tuples or raise error
        """
        threshold_output = []
        feature_label, threshold = list(ExpressionQueryTool.validate_threshold_object(threshold_input[0]))
        if not all([threshold, feature_label]):
            raise ValueError("invalid threshold object")

        for threshold_obj in threshold_input:
            if all(k in threshold_obj for k in ['threshold', feature_label]):
                threshold_output.append((threshold_obj[feature_label], threshold_obj['threshold']))
            else:
                raise ValueError("invalid threshold object")
        return threshold_output

    @staticmethod
    def validate_threshold_object(threshold_obj):
        """
        Returns a tuple of threshold object values or None if invalid
        """
        try:
            threshold = threshold_obj.get('threshold', '')
            float(threshold)
        except ValueError:
            threshold = None
        if 'featureName' in threshold_obj:
            feature_label = 'featureName'
        elif 'featureID' in threshold_obj:
            feature_label = 'featureID'
        else:
            feature_label = None
        return feature_label, threshold

    @staticmethod
    def decode_h5_array(input_array):
        decoded = map(bytes.decode, input_array)
        return list(decoded)
