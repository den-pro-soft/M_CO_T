import React, { Component } from 'react';
import _ from 'lodash';
import msgbox from '../shared/msgbox';
import dates from '../shared/dates';
import numbers from '../shared/numbers';
import ajax from '../shared/ajax';
import handleInputChange from '../shared/handleInputChange';
import redirectTo from '../shared/redirectTo';
import Scrollbars from './Scrollbars';
import FileUpload from './FileUpload';
import DatePickerInput from './DatePickerInput';
import AjaxError from './AjaxError';
import UnsavedDataHandler from './UnsavedDataHandler';
import travellerDataXlsx from '../files/Traveller data.xlsx';


class PreviousUploads extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: undefined,
      filterTaxYear: "",
    };
    this.fileUploadRefs = {};
    this.pristineData = undefined;
    this.handlePeriodDateInputChange = this.handlePeriodDateInputChange.bind(this);
    this.onTravellerDataUploadCompleted = this.onTravellerDataUploadCompleted.bind(this);
    this.save = this.save.bind(this);
    this.handleInputChange = handleInputChange.bind(this);
    this.renderPeriod = this.renderPeriod.bind(this);
  }

  componentDidMount() {
    this.fetchData();
  }

  save(event) {
    event.preventDefault();
    const data = this.state.data;
    ajax.exec('traveller-data/periods', 'PUT', data, event.target).then(() => {
      msgbox.alert("The traveller data has been successfully saved.").then(() => {
        redirectTo('/assumptions');
      });
    });
  }

  canSave() {
    const previousUploadsModified = !_.isEqual(this.pristineData, this.state.data);
    return previousUploadsModified;
  }

  fetchData() {
    this.setState({ data: undefined, filterTaxYear: "all" });
    ajax.exec('traveller-data/periods')
      .then(previousUploads => {
        if (!previousUploads) {
          previousUploads = [];
        }
        const data = previousUploads;
        let filterTaxYear;
        previousUploads.forEach(period => {
          period.originalFrom = period.from;
          period.originalTo = period.to;
          const taxYears = dates.getTaxYearsFrom(period.originalFrom, period.originalTo);
          taxYears.forEach(taxYear => {
            if (taxYear) {
              if (!filterTaxYear || filterTaxYear < taxYear) {
                filterTaxYear = taxYear;
              }
            }
          });
        });
        this.pristineData = _.cloneDeep(data);
        this.setState({ data, filterTaxYear: filterTaxYear || "all" });
      })
      .catch(() => this.setState({ data: null }));
  }

  handlePeriodDateInputChange(eventOrValue, period, field) {
    period[field] = eventOrValue && eventOrValue.target ? eventOrValue.target.value : eventOrValue;
    const from = dates.parse(period.from);
    const to = dates.parse(period.to);
    period.invalid = from && to && to.isBefore(from);
    const data = this.state.data;
    this.setState({ data });
  }

  removePeriod(period) {
    msgbox.confirm(`Do you really want to remove the data for the period ${dates.formatDate(period.from)} to ${dates.formatDate(period.to)}?`).then(() => {
      const data = this.state.data;
      const previousUploads = data;
      previousUploads.splice(previousUploads.indexOf(period), 1);
      this.setState({ data });
    });
  }

  uploadTravellerData(period) {
    this.fileUploadRefs[period.id].open();
  }

  downloadTravellerData(travellerData, event) {
    ajax.download(`traveller-data/${travellerData.id}`, travellerData.filename, event.target);
  }

  onTravellerDataUploadStarted(period) {
    period.dirtyTravellerData = true;
    const data = this.state.data;
    this.setState({ data });
  }

  onTravellerDataUploadCompleted(res, period) {
    const travellerData = res[res.length - 1];
    if (travellerData) {
      const applyTravellerData = () => {
        if (travellerData.errorCount > 0) {
          msgbox.alert(`${travellerData.errorCount} warning(s) were found while processing the travel data. ` +
                      'Please go to Additional Clarifications in order to check them.');
        }
        period.travellerData = travellerData;
        const data = this.state.data;
        this.setState({ data });
      };
      const tripsBefore = travellerData.tripsBeforePeriod;
      const tripsAfter = travellerData.tripsAfterPeriod;
      if (tripsBefore || tripsAfter) {
        let trips = '';
        if (tripsBefore) {
          trips = `${tripsBefore} ${tripsBefore == 1 ? 'trip' : 'trips'} before`;
        }
        if (travellerData.tripsAfterPeriod) {
          if (trips) {
            trips += ' and ';
          }
          trips += `${tripsAfter} ${tripsAfter == 1 ? 'trip' : 'trips'} after`;
        }
        msgbox.alert(`We noticed your traveller data spreadsheet contains ${trips} the informed ` +
                     'report period. Please note that saving this data may impact existing report runs.').then(applyTravellerData);
      } else {
        applyTravellerData();
      }
    }
  }

  renderButtonsCell(period) {

    let buttonsCell = [
      <button type="button" className="btn btn-sm btn-default" onClick={() => this.uploadTravellerData(period)} key="upload-data-button">
        <i className="glyphicon glyphicon-upload" />
        {' '}{period.travellerData ? "Amend" :"Upload"}
      </button>
    ];

    if (period.travellerData) {
      buttonsCell.push(' ');
      buttonsCell.push((
        <button className="btn btn-sm btn-default" onClick={e => this.downloadTravellerData(period.travellerData, e)} key="download-data-button">
          <i className="glyphicon glyphicon-download" />
          {' '}Download
        </button>
      ));
    }

    return buttonsCell;    
  }

  renderPeriod(period) {
    const dirtyTravellerData = period.dirtyTravellerData;
    const from = dates.parse(period.from);
    const to = dates.parse(period.to);
    return (
      <tr key={`period-${period.id}`}>
        <td className="mintax-vmiddle" style={{ display: dirtyTravellerData ? 'none' : undefined }}>
          {period.travellerData ? period.travellerData.filename : "-"}
        </td>
        <td className="mintax-vmiddle" style={{ display: dirtyTravellerData ? 'none' : undefined }}>
          {period.travellerData ? dates.formatDateTime(period.travellerData.dateUploaded) : "-"}
        </td>
        <td className="mintax-vmiddle" style={{ display: dirtyTravellerData ? undefined : 'none' }} colSpan={2}>
          <FileUpload minimal={true}
              dropzoneRef={ref => this.fileUploadRefs[period.id] = ref}
              to="traveller-data"
              extraData={{ from: period.from, to: period.to }}
              onUploadStarted={() => this.onTravellerDataUploadStarted(period)}
              onBatchCompleted={batch => this.onTravellerDataUploadCompleted(batch, period)} />
        </td>
        <td className={`mintax-datepicker-cell-fixer ${period.invalid ? "mintax-invalid-cell" : ""}`}>
          <DatePickerInput className="form-control"
                  selected={from}
                  onChange={value => this.handlePeriodDateInputChange(value, period, 'from')}
                  onChangeRaw={event => this.handlePeriodDateInputChange(event, period, 'from')} />
        </td>
        <td className={`mintax-datepicker-cell-fixer ${period.invalid ? "mintax-invalid-cell" : ""}`}>
          <DatePickerInput className="form-control"
                  selected={to}
                  onChange={value => this.handlePeriodDateInputChange(value, period, 'to')}
                  onChangeRaw={event => this.handlePeriodDateInputChange(event, period, 'to')} />
        </td>
        { period.travellerData ? (
          <td className="mintax-vmiddle">
            <span className="mintax-success">
              {period.travellerData.entryCount} trip{period.travellerData.entryCount == 1 ? "" : "s"}
            </span>
          </td>
        ) : (
          <td className="mintax-danger mintax-vmiddle">Incomplete</td>
        )}
        <td className="mintax-vmiddle">
          { period.travellerData.outsidePeriodCount > 0 ? (
            <span className="mintax-danger">
              {period.travellerData.outsidePeriodCount} trip{period.travellerData.outsidePeriodCount == 1 ? "" : "s"}
            </span>
          ) : "0 trips" }
        </td>
        <td className="mintax-vmiddle">
          { period.travellerData.invalidCount > 0 ? (
              <span className="mintax-danger">
                {period.travellerData.invalidCount} trip{period.travellerData.invalidCount == 1 ? "" : "s"}
              </span>
            ) : "0 trips" }
        </td>
        <td className="mintax-actions-column">
          {this.renderButtonsCell(period)}
          {' '}
          <button type="button" className="btn btn-sm btn-default" onClick={() => this.removePeriod(period)}><i className="glyphicon glyphicon-trash" /></button>
        </td>
        <td className="mintax-actions-column">
        </td>
      </tr>
    );
  }

  renderPeriods() {
    const periods = this.state.data;
    const filteredPeriods = periods.filter(period => {
      const taxYears = dates.getTaxYearsFrom(period.originalFrom, period.originalTo);
      for (const taxYear in taxYears) {
        if (!taxYear || this.state.filterTaxYear == 'all') {
          return true;
        } else {
          return taxYears.indexOf(parseInt(this.state.filterTaxYear)) >= 0;
        }
      }
    });
    return filteredPeriods.map(this.renderPeriod);
  }

  renderTaxYearsOptions() {
    const taxYears = new Set();
    this.state.data.forEach(period => {
      dates.getTaxYearsFrom(period.originalFrom, period.originalTo).forEach(taxYear => {
        if (taxYear) {
          taxYears.add(taxYear);
        }
      });
    });
    return Array.from(taxYears).sort().map(taxYear => (
        <option key={taxYear} value={taxYear}>{taxYear}/{(parseInt(taxYear) + 1) % 100}</option>
      )).reverse();
  }

  renderPreviousUploads() {
    let atLeastOneInvalid = this.state.data.filter(period => period.invalid).length > 0;
    return (
      <div className="mintax-form">
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="row">
              <div className="col-xs-12">
                <select className="form-control mintax-small-field" name="filterTaxYear"
                      value={this.state.filterTaxYear}
                      onChange={this.handleInputChange}>
                  {this.renderTaxYearsOptions()}
                  <option value="all">All Tax Years</option>
                </select>
              </div>
            </div>
            <div className="row">
              <div className="col-xs-12">
                <table className="table table-bordered table-striped table-condensed">
                  <thead>
                    <tr>
                      <th style={{ width: "210pt", minWidth: "210pt" }} rowSpan={2}>Spreadsheet Name</th>
                      <th style={{ width: "120pt", minWidth: "120pt" }} rowSpan={2}>Date Uploaded</th>
                      <th colSpan={2}>Dates</th>
                      <th style={{ width: "90pt", minWidth: "90pt" }} rowSpan={2}>Number of trips</th>
                      <th style={{ width: "90pt", minWidth: "90pt" }} rowSpan={2}>Outside Period</th>
                      <th style={{ width: "90pt", minWidth: "90pt" }} rowSpan={2}>Incomplete / Invalid</th>
                      <th rowSpan={2} style={{ width: "10pt", minWidth: "10pt" }} className="mintax-actions-column"></th>
                      <th rowSpan={2} className="mintax-actions-column"></th>
                    </tr>
                    <tr>
                      <th style={{ width: "100pt", minWidth: "100pt" }}>From</th>
                      <th style={{ width: "100pt", minWidth: "100pt" }}>
                        To
                        {' '}
                        {atLeastOneInvalid ? (
                          <span className="mintax-danger glyphicon glyphicon-ban-circle"
                                title="To date must be equal or after From date" />
                        ) : <span />}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {this.renderPeriods()}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group">
            <button className="btn btn-primary"
                    onClick={this.save}
                    disabled={!this.canSave()}
                    title={this.canSave() ? "" : "There is no unsaved changes"}>Save</button>
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
        <UnsavedDataHandler verifier={() => !_.isEqual(this.pristineData, this.state.data)} />
      </div>
    );
  }

  render() {

    if (this.state.data === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data === null) {
      return <AjaxError />
    }

    return this.renderPreviousUploads();
  }
}

export default PreviousUploads;
