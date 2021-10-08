# CanCOGeN Dashboard

This is a react.js-based visualization dashboard that provides visualizations on clinical, genomic data for the CanCOGeN project. You may learn more about the CanCOGeN initiative from [here](https://www.genomecanada.ca/en/cancogen).

### Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Dataset selection](#dataset-selection)
  - [Available pages](#available-pages)
- [Contributing to this project](#contributing-to-this-project)
- [GitHub workflow](#github-workflow)


## Installation

Before installing the Dashboard, make sure you have [Node.js](https://nodejs.org/en/) version v10.13.0 or above and [Yarn](https://yarnpkg.com/) installed on your environment.

Clone this repository and start the installation using the following commands:
```bash
git clone git@github.com:CanDIG/cancogen_dashboard.git
cd cancogen_dashboard
yarn install
```
These commands will install all the dependencies used in the application. Next, specify the URLs of the backend CanCOGen services:
```bash
export REACT_APP_BASE_URL='http://ga4ghdev01.bcgsc.ca:20127'
export REACT_APP_METADATA_URL='http://ga4ghdev01.bcgsc.ca:4000'
export REACT_APP_HTSGET_URL='http://ga4ghdev01.bcgsc.ca:3333'
export REACT_APP_DRS_URL='http://ga4ghdev01.bcgsc.ca:5000'
export REACT_APP_FEDERATION_URL='http://ga4ghdev01.bcgsc.ca:8890/federation/search'
```

**The following variable only needs to be exported for GSC specific deployments to comply with internal routing.**
Site Specific Environmental Variables:
```bash
export REACT_APP_LOCATION='GSC'
```


Once the installation is completed, you may start the dashboard using:
```bash
yarn start
```

## Usage

### Dataset selection

For pages with data sources of multiple datasets, you may switch datasets in the top right corner.

![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/datasets_dropdown.png)

### Available pages

Below there is a list of screenshots of selected pages. Click on the picture to expand it.

| ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/overview_page.png)        | ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/htsget_browser.png) |
|------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/individuals_overview.png) | ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/gwas_browser.png)      |
| ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/variants_search.png)      | ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/symptoms_search.png) |
| ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/chord_metadata.png)       |   ![](https://raw.githubusercontent.com/CanDIG/cancogen_dashboard/develop/docs/services_status.png)                                                                                                              |

## Contributing to this project

If you encounter a bug, or have a problem of using the service, please contact us by opening an issue at [issues page](https://github.com/CanDIG/cancogen_dashboard/issues)

### GitHub workflow

We mainly employ three different types of branches: feature branches, develop branch, and stable branch.

Feature branches are used to resolve a limited set of issues, and typically follows the naming convention of username/fix_one_particular_issue. When initiating a Pull Request, you should request it to be merged back into the develop branch. The commits in individual feature branches are usually squashed, and code review usually happens at this step.

Develop branch is used to host code that has passed all the tests, but may not yet be production-ready, As a developer, you are welcome to play with this branch to test some of the new functionalities.

If you would like to contribute code, please fork the package to your own git repository, then initiate a Pull Request to be merged into develop.

