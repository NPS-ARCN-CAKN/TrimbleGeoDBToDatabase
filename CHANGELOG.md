# ChangeLog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

This project adheres to the spirit of the major/minor versioning
scheme as implemented by the
[openSUSE project](https://en.opensuse.org/openSUSE:Versioning_scheme).

## [Unreleased]
### Added
- Add parameter `UpdateLatLongOnly` to function
  `ExportContinuousJoined`. This applies to which retrieval columns
  are updated.

- Add latitude/longitude only columns (in function
  `ExportContinuousJoined`) to SQL retrieval update statement options.
  This handles the case where retrieval dates and times (and possible
  notes) have been already entered.
  
### Changed

- Update the date comparison conditions in function
  `ExportContinuousJoined` so that the date variables are all objects,
  rather then comparing strings.
  
- Revised notes to function `ExportContinuousJoined`.

### Removed

- Remove the code in function `ExportContinuousJoined` that requires
  the `csv.DictReader`. Revised the Trimble python code to handle the
  retrieval based on `SiteName` and `DateRetrieved` columns instead of
  `SiteName` and `DateDeployed`.

- Remove the the code that required the `DeployedCSV` argument in
  function `ExportContinuousJoined`. Even though values `SiteName` and
  `DateRetrieved` are not guaranteed (in the system) to be unique
  (although, theorectically, there is an argument for this extra
  constraint). In practice this is not an issue. And after generating
  the SQL retrieval (or deployed) UPDATE code, these values can be
  compared to what is in the database for accuracy before upload.

- Remove `mapDeployed` dictionary in function
  `ExportContinuousJoined`. This idea behind this dictionary was
  enable the retrieval of the database deploy date for a particular
  site name; assuming the entered database date was superior to the
  Trimble recorded date; this means though, that the imput to the
  dictionary has a unique number of sitenames. This dictionary was
  also used to retrieve the deploy date for the retrieval SQL UPDATE
  script; but in practice, we may use the retieval date and sitename
  as unique values.

- Remove function `CSVDictToKeyedDict` from function
  `ExportContinuousJoined`.
  
- Remove the functions `AssertRetrieved` and `AssertDeplotyed`. No
  longer necessary after the parameter `DeployCSV` was removed.
  
## [2.0] - 2024-11-12

## [1.3] - 2024-03-07

## [1.2] - 2023-02-21

## [1.1] - 2021-01-26

Extensive revison by Nick Bywater.

## [1.0] - 2021-10-14

Initial release by Scott Miller.
