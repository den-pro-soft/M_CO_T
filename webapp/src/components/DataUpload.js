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


const newPeriod = function() {
  return {
    id: numbers.guid(),
    from: null,
    to: null,
    travellerData: null,
  };
};

class DataUpload extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: newPeriod(),
    };
    this.fileUploadRefs = {};
    this.dropzoneRefs = {};
    this.pristineData = _.cloneDeep(this.state.data);
    this.handlePeriodDateInputChange = this.handlePeriodDateInputChange.bind(this);
    this.onTravellerDataUploadCompleted = this.onTravellerDataUploadCompleted.bind(this);
    this.save = this.save.bind(this);
    this.handleInputChange = handleInputChange.bind(this);
  }

  save(event) {
    event.preventDefault();
    const data = this.state.data;
    ajax.exec('traveller-data/periods', 'POST', data, event.target).then(() => {
      msgbox.alert("The traveller data has been successfully saved.").then(() => {
        redirectTo('/assumptions');
      });
    });
  }

  canSave() {
    const newPeriodModified = !_.isEqual(this.pristineData, this.state.data);
    const newPeriodHasTravellerData = this.state.data.travellerData;
    return newPeriodModified && newPeriodHasTravellerData;
  }

  handlePeriodDateInputChange(eventOrValue, period, field) {
    period[field] = eventOrValue && eventOrValue.target ? eventOrValue.target.value : eventOrValue;
    const from = dates.parse(period.from);
    const to = dates.parse(period.to);
    period.invalid = from && to && to.isBefore(from);
    const data = this.state.data;
    this.setState({ data });
  }

  uploadTravellerData(period) {
    this.dropzoneRefs[period.id].open();
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

  renderUploadForm() {
    const period = this.state.data;
    return (
      <div className="mintax-form">
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="row">
              <div className="col-xs-12">
                <p>
                  Please complete and upload the
                  {' '}<a className="mintax-pointer" href={travellerDataXlsx} download>traveller data template</a>.
                </p>
              </div>
            </div>
            <div className="row">
              <div className="col-xs-12">
                <table className="table table-bordered table-striped table-condensed">
                  <thead>
                    <tr>
                      <th colSpan={2}>Dates</th>
                      <th style={{ width: "90pt", minWidth: "90pt" }} rowSpan={2}>Status</th>
                      <th rowSpan={2} style={{ width: "10pt", minWidth: "10pt" }} className="mintax-actions-column"></th>
                      <th rowSpan={2} className="mintax-actions-column"></th>
                    </tr>
                    <tr>
                      <th style={{ width: "100pt", minWidth: "100pt" }}>From</th>
                      <th style={{ width: "100pt", minWidth: "100pt" }}>
                        To
                        {' '}
                        {period.invalid ? (
                          <span className="mintax-danger glyphicon glyphicon-ban-circle"
                                title="To date must be equal or after From date" />
                        ) : <span />}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className={`mintax-datepicker-cell-fixer ${period.invalid ? "mintax-invalid-cell" : ""}`}>
                        <DatePickerInput className="form-control"
                                selected={dates.parse(period.from)}
                                onChange={value => this.handlePeriodDateInputChange(value, period, 'from')}
                                onChangeRaw={event => this.handlePeriodDateInputChange(event, period, 'from')} />
                      </td>
                      <td className={`mintax-datepicker-cell-fixer ${period.invalid ? "mintax-invalid-cell" : ""}`}>
                        <DatePickerInput className="form-control"
                                selected={dates.parse(period.to)}
                                onChange={value => this.handlePeriodDateInputChange(value, period, 'to')}
                                onChangeRaw={event => this.handlePeriodDateInputChange(event, period, 'to')} />
                      </td>
                      <td className={ period.travellerData ? "mintax-success mintax-vmiddle" : "mintax-danger mintax-vmiddle" }>
                        { period.travellerData ?
                            `${period.travellerData.entryCount} trip${period.travellerData.entryCount == 1 ? "" : "s"}` :
                            "Incomplete" }
                      </td>
                      <td className="mintax-actions-column">
                        {this.renderButtonsCell(period)}
                      </td>
                      <td className="mintax-actions-column">
                        <FileUpload minimal={true}
                                    ref={ref => this.fileUploadRefs[period.id] = ref}
                                    dropzoneRef={ref => this.dropzoneRefs[period.id] = ref}
                                    to="traveller-data"
                                    extraData={{ from: period.from, to: period.to }}
                                    onBatchCompleted={batch => this.onTravellerDataUploadCompleted(batch, period)} />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group-right">
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

    return this.renderUploadForm();
  }
}

export default DataUpload;
