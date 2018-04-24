import React, { Component } from 'react';
import UnsavedDataHandler from './UnsavedDataHandler';
import _ from 'lodash';
import ajax from '../shared/ajax';
import msgbox from '../shared/msgbox';
import dates from '../shared/dates';
import collections from '../shared/collections';
import Scrollbars from './Scrollbars';
import AjaxError from './AjaxError';
import DatePickerInput from './DatePickerInput';
import Select from 'react-select';
import TimeInput from './TimeInput';
import PagingControls from './PagingControls';


const newClarification = function () {
  return {
    homeCountry: "",
    fromDate: null,
    toDate: null,
  };
};


class AdditionalClarifications extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeTab: 'summary',
      data: undefined,
      countries: undefined,
      showUKTouchingOnly: true,
      showUnansweredInboundAssumptionsOnly: true,
      showUnansweredOutboundAssumptionsOnly: true,
      showUnansweredUnclearBorderCrossOnly: true,
      showUnansweredDuplicateIDsOnly: true,
      showDupUKTouchingOnly: true,
      unclearHomeCountryCurrentPage: 0,
      incompleteTripsCurrentPage: 0,
      assumedInboundCurrentPage: 0,
      assumedOutboundCurrentPage: 0,
      unclearBorderCrossCurrentPage: 0,
      duplicateIDsCurrentPage: 0,
      ignoredEmployeesCurrentPage: 0,
      ignoredTripsCurrentPage: 0,
    };
    this.pristineData = undefined;
    this.handleDataInputChange = this.handleDataInputChange.bind(this);
    this.handleDateInputChange = this.handleDateInputChange.bind(this);
    this.handleShowUKTouchingOnlyChange = this.handleShowUKTouchingOnlyChange.bind(this);
    this.handleUnansweredInboundAssumptionsOnlyChange = this.handleUnansweredInboundAssumptionsOnlyChange.bind(this);
    this.handleUnansweredOutboundAssumptionsOnlyChange = this.handleUnansweredOutboundAssumptionsOnlyChange.bind(this);
    this.handleUnansweredUnclearBorderCrossChange = this.handleUnansweredUnclearBorderCrossChange.bind(this);
    this.handleUnansweredDuplicateIDsOnlyChange = this.handleUnansweredDuplicateIDsOnlyChange.bind(this);
    this.handleDuplicateShowUKTouchingOnlyChange = this.handleDuplicateShowUKTouchingOnlyChange.bind(this);
    this.send = this.send.bind(this);
  }

  componentDidMount() {
    this.fetchData();
    this.fetchCountries();
  }

  fetchData() {
    this.setState({ data: undefined });
    ajax.exec('additional-clarifications')
      .then(data => {
        data.inboundAssumptions.forEach(trip => {
          trip.originalInboundAssumptionConfirmed = trip.inboundAssumptionConfirmed;
        });
        data.outboundAssumptions.forEach(trip => {
          trip.originalOutboundAssumptionConfirmed = trip.outboundAssumptionConfirmed;
        });
        data.unclearBorderCrossTime.forEach(trip => {
          trip.originalCorrectTime = trip.correctTime;
        });
        data.incompleteTrips.forEach(trip => {
          trip.originalOriginCountry = trip.originCountry;
          trip.originalDestinationCountry = trip.destinationCountry;
        });
        data.unclearHomeCountry.forEach(emp => {
          if (emp.clarifications.length == 0) {
            emp.clarifications.push(newClarification());
          }
        });
        data.duplicateIDs.forEach(dup => {
          dup.originalConfirmed = dup.confirmed;
          dup.originalOriginCountry = dup.originCountry;
          dup.originalDestinationCountry = dup.destinationCountry;
        });
        this.pristineData = _.cloneDeep(data);
        this.setState({
          data,
          unclearHomeCountryCurrentPage: 0,
          incompleteTripsCurrentPage: 0,
          assumedInboundCurrentPage: 0,
          assumedOutboundCurrentPage: 0,
          unclearBorderCrossCurrentPage: 0,
        });
      }, () => {
        this.setState({ data: null });
      });
  }

  fetchCountries() {
    return ajax.exec('countries').then(countries => {
      this.setState({
        countries: countries.map(country => {
          return {
            value: country.code,
            label: `${country.code} - ${country.name}`,
          };
        })
      });
    });
  }

  send(event) {
    event.preventDefault();
    const data = this.state.data;
    ajax.exec('additional-clarifications', 'PUT', data, event.target).then(() => {
      msgbox.alert("Your clarificiations have been successfully saved.").then(() => {
        this.fetchData();
      });
    });
  }

  handleShowUKTouchingOnlyChange(event) {
    this.setState({
      showUKTouchingOnly: event.target.checked,
      incompleteTripsCurrentPage: 0
    });
  }
  
  handleUnansweredInboundAssumptionsOnlyChange(event) {
    this.setState({
      showUnansweredInboundAssumptionsOnly: event.target.checked,
      assumedInboundCurrentPage: 0
    });
  }
  
  handleUnansweredOutboundAssumptionsOnlyChange(event) {
    this.setState({
      showUnansweredOutboundAssumptionsOnly: event.target.checked,
      assumedOutboundCurrentPage: 0
    });
  }
  
  handleUnansweredUnclearBorderCrossChange(event) {
    this.setState({
      showUnansweredUnclearBorderCrossOnly: event.target.checked,
      unclearBorderCrossCurrentPage: 0
    });
  }

  handleUnansweredDuplicateIDsOnlyChange(event) {
    this.setState({
      showUnansweredDuplicateIDsOnly: event.target.checked,
      duplicateIDsCurrentPage: 0
    });
  }

  handleDuplicateShowUKTouchingOnlyChange(event) {
    this.setState({
      showDupUKTouchingOnly: event.target.checked,
      duplicateIDsCurrentPage: 0
    });
  }

  handleDataInputChange(fieldName, subject, event) {
    const target = event.target;
    const type = target.type;
    const data = this.state.data;
    subject[fieldName] = type === 'checkbox' ? target.checked : target.value;
    this.setState({ data });
  }
  
  handleDateInputChange(eventOrValue, subject, field) {
    subject[field] = eventOrValue && eventOrValue.target ? eventOrValue.target.value : eventOrValue;
    const data = this.state.data;
    this.setState({ data });
  }
  
  handleCountryChange(subject, field, selection) {
    subject[field] = selection ? selection.value : null;
    const data = this.state.data;
    this.setState({ data });
  }

  deleteHomeCountryClarification(employee, clar) {
    if (employee.clarifications.length > 1) {
      employee.clarifications.splice(employee.clarifications.indexOf(clar), 1);
      if (employee.clarifications.length == 1) {
        employee.clarifications[0].fromDate = null;
        employee.clarifications[0].toDate = null;
      }
    } else {
      clar.homeCountry = "";
      clar.fromDate = null;
      clar.toDate = null;
    }
    const data = this.state.data;
    this.setState({ data });
  }

  toggleChangeInMultipleHomeCountries(employee) {
    const data = this.state.data;
    if (employee.clarifications.length == 1) {
      employee.clarifications.push(newClarification());
      this.setState({ data });
    } else {
      msgbox.confirm('This will remove all but the first clarification for ' +
                     `employee ${employee.travellerName || 'Unnamed'} (${employee.employeeId || 'no ID'}). ` +
                     'Are you sure you want to proceed?').then(() => {
        employee.clarifications.splice(1);
        employee.clarifications[0].fromDate = null;
        employee.clarifications[0].toDate = null;
        this.setState({ data });
      });
    }
  }

  toggleChangeInDuplicateIDConfirmation(event, group) {
    const checked = event.target.checked;
    for (let idx in group) {
      group[idx].confirmed = checked;
    }
    const data = this.state.data;
    this.setState({ data });
  }

  toggleIgnoreBorderCrossTrips(tripGroup) {
    tripGroup.forEach(trip => {
      trip.ignore = !trip.ignore;
    });
    const data = this.state.data;
    this.setState({ data });
  }

  addHomeCountryClarification(employee, after) {
    const idx = employee.clarifications.indexOf(after);
    employee.clarifications.splice(idx + 1, 0, newClarification());
    const data = this.state.data;
    this.setState({ data });
  }

  hasPendingChanges() {
    return !_.isEqual(this.pristineData, this.state.data);
  }

  getFilteredIncompleteTrips() {
    const showUKTouchingOnly = this.state.showUKTouchingOnly;
    return this.state.data.incompleteTrips.filter(trip => {
      const touchesUK = (!trip.originalOriginCountry || trip.originalOriginCountry == 'GBR') ||
                        (!trip.originalDestinationCountry || trip.originalDestinationCountry == 'GBR');
      return !showUKTouchingOnly || touchesUK;
    });
  }

  getFilteredInboundAssumptions() {
    const showUnansweredInboundAssumptionsOnly = this.state.showUnansweredInboundAssumptionsOnly;
    return this.state.data.inboundAssumptions.filter(trip => {
      const unanswered = !trip.originalInboundAssumptionConfirmed;
      return !showUnansweredInboundAssumptionsOnly || unanswered;
    });
  }
  
  getFilteredOutboundAssumptions() {
    const showUnansweredOutboundAssumptionsOnly = this.state.showUnansweredOutboundAssumptionsOnly;
    return this.state.data.outboundAssumptions.filter(trip => {
      const unanswered = !trip.originalOutboundAssumptionConfirmed;
      return !showUnansweredOutboundAssumptionsOnly || unanswered;
    });
  }
  
  getUnclearBorderCrossTimeGroups() {
    const unclearBorderCrossTrips = this.state.data.unclearBorderCrossTime;
    const keyGetter = trip => `${trip.travellerName}-${trip.employeeId}-${trip.borderCross}`;
    return Object.values(collections.groupBy(unclearBorderCrossTrips, keyGetter));
  }
  
  getFilteredUnclearBorderCrossTimeGroups(tripGroups) {
    const showUnansweredUnclearBorderCrossOnly = this.state.showUnansweredUnclearBorderCrossOnly;
    return tripGroups.filter(group => {
      let unanswered = false;
      group.forEach(trip => {
        if (!trip.originalCorrectTime) {
          unanswered = true;
        }
      });
      return !showUnansweredUnclearBorderCrossOnly || unanswered;
    });
  }

  getDuplicateIDGroups() {
    const duplicateIDs = this.state.data.duplicateIDs;
    const keyGetter = duplicate => duplicate.effectiveEmployeeId;
    return Object.values(collections.groupBy(duplicateIDs, keyGetter));
  }

  getFilteredDupĺicateIDGroups(groups) {
    const showUnansweredDuplicateIDsOnly = this.state.showUnansweredDuplicateIDsOnly;
    return groups.filter(group => {
      let unanswered = false;
      group.forEach(trip => {
        if (!trip.originalConfirmed) {
          unanswered = true;
        }
      });
      return !showUnansweredDuplicateIDsOnly || unanswered;
    });
  }

  getFilteredDupShowUk(groups) {
    const showDupUKTouchingOnly = this.state.showDupUKTouchingOnly;
    return groups.filter((group,idx) => {
      let flg = false;
      if(showDupUKTouchingOnly == true)
      {
        for (var i = 0; i < group.length; i ++)
        {
          for(var j = 0; j < group[i].originalOriginCountry.length; j ++)
          {
            if(group[i].originalOriginCountry[j] == 'GBR'){
              flg = true;
              break;
            }
          }
          if(flg == false)
          {
            for(var j = 0; j < group[i].originalDestinationCountry.length; j ++)
            {
              if(group[i].originalDestinationCountry[j] == 'GBR'){
                flg = true;
                break;
              }
            }
          }
          if(flg == false)
            group.splice(i, 1);
        }
        if(group.length == 1){
          groups.splice(idx, 1);
          return false;
        }
        return true;
      }
      else
        return true;
    }); 
  }

  renderUnclearHomeCountryCells(clar, employee) {
    return [
      <td key="country">
        <Select value={clar.homeCountry}
          onChange={selection => this.handleCountryChange(clar, 'homeCountry', selection)}
          isLoading={this.state.countries === undefined}
          options={this.state.countries} />
      </td>,
      <td key="effective-from" className="mintax-datepicker-cell-fixer">
        <DatePickerInput className="form-control" disabled={employee.clarifications.length == 1}
                  selected={dates.parse(clar.fromDate)}
                  onChange={value => this.handleDateInputChange(value, clar, 'fromDate')}
                  onChangeRaw={event => this.handleDateInputChange(event, clar, 'fromDate')} />
      </td>,
      <td key="effective-to" className="mintax-datepicker-cell-fixer">
        <DatePickerInput className="form-control" disabled={employee.clarifications.length == 1}
                  selected={dates.parse(clar.toDate)}
                  onChange={value => this.handleDateInputChange(value, clar, 'toDate')}
                  onChangeRaw={event => this.handleDateInputChange(event, clar, 'toDate')} />
      </td>,
      <td className="mintax-actions-column" key="actions">
        {employee.clarifications.length > 1 ? (
            <button type="button" className="btn btn-sm btn-default" onClick={() => this.addHomeCountryClarification(employee, clar)}>
              <span className="glyphicon glyphicon-plus" />
            </button>
          ) : <span />}
        {' '}
        <button type="button" className="btn btn-sm btn-default"
                onClick={() => this.deleteHomeCountryClarification(employee, clar)}><i className="glyphicon glyphicon-trash" /></button>
      </td>
    ];
  }

  renderSummaryTab() {
    const summaryData = this.getSummaryData();
    const globalData = {
      total: summaryData.map(x => x.totalClarifications).reduce((a, b) => a + b, 0),
      completed: summaryData.map(x => x.completed).reduce((a, b) => a + b, 0)
    };
    return (
      <div>
        <table className="table table-bordered">
          <thead>
            <tr>
              <th style={{ width: 300 }}>Category</th>
              <th className="text-right" style={{ width: 175 }}>Total Clarifications</th>
              <th className="text-right" style={{ width: 105 }}>Completed</th>
              <th className="text-right" style={{ width: 105 }}>Incomplete</th>
              <th className="mintax-actions-column"></th>
            </tr>
          </thead>
          <tbody>
            {summaryData.map(summaryRow => (
              <tr key={summaryRow.tab}>
                <td>
                  <a className="mintax-pointer" onClick={() => this.setState({ activeTab: summaryRow.tab })}>
                    {summaryRow.category}
                  </a>
                </td>
                <td className="text-right">{summaryRow.totalClarifications}</td>
                <td className={summaryRow.completed > 0 ? 'mintax-success text-right' : 'text-right'}>{summaryRow.completed}</td>
                <td className={summaryRow.completed < summaryRow.totalClarifications ? 'mintax-danger text-right' : 'text-right'}>{summaryRow.totalClarifications - summaryRow.completed}</td>
                <td className="mintax-actions-column"></td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td>Total</td>
              <td>{globalData.total}</td>
              <td className={globalData.completed > 0 ? 'mintax-success' : ''}>
                {globalData.completed}
              </td>
              <td className={globalData.completed < globalData.total ? 'mintax-danger' : ''}>
                {globalData.total - globalData.completed}
              </td>
            </tr>
          </tfoot>
        </table>
        <table className="table table-bordered">
          <thead>
            <tr>
              <th style={{ width: 300 }}>Ignored Records</th>
              <th className="text-right" style={{ width: 175 }}>Total Ignored</th>
              <th className="mintax-actions-column"></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <a className="mintax-pointer" onClick={() => this.setState({ activeTab: 'ignored-employees' })}>
                  Employees
                </a>
              </td>
              <td className="text-right">{this.state.data.ignoredEmployees.length}</td>
            </tr>
            <tr>
              <td>
                <a className="mintax-pointer" onClick={() => this.setState({ activeTab: 'ignored-trips' })}>
                  Trips
                </a>
              </td>
              <td className="text-right">{this.state.data.ignoredTrips.length}</td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }

  getSummaryData() {

    const data = this.state.data;
    const summaryData = [];

    summaryData.push({
      tab: 'unclear-home-country',
      category: 'Unclear Home Country',
      totalClarifications: data.unclearHomeCountry.length,
      completed: data.unclearHomeCountry.filter(x => 
        x.clarifications.filter(c => c.homeCountry != "").length > 0).length,
    });

    summaryData.push({
      tab: 'incomplete-trips',
      category: 'Incomplete Trips',
      totalClarifications: data.incompleteTrips.length,
      completed: 0,
    });
    
    summaryData.push({
      tab: 'assumed-inbound',
      category: 'Assumed Inbound Trips',
      totalClarifications: data.inboundAssumptions.length,
      completed: data.inboundAssumptions.filter(x => x.inboundAssumptionConfirmed).length,
    });
    
    summaryData.push({
      tab: 'assumed-outbound',
      category: 'Assumed Outbound Trips',
      totalClarifications: data.outboundAssumptions.length,
      completed: data.outboundAssumptions.filter(x => x.outboundAssumptionConfirmed).length,
    });
    
    summaryData.push({
      tab: 'unclear-border-cross-time',
      category: 'Unclear Border Cross Time',
      totalClarifications: data.unclearBorderCrossTime.length,
      completed: data.unclearBorderCrossTime.filter(x => x.correctTime).length,
    });
    
    const duplicateIDsGroups = this.getDuplicateIDGroups();
    summaryData.push({
      tab: 'duplicate-ids',
      category: 'Duplicate IDs',
      totalClarifications: duplicateIDsGroups.length,
      completed: duplicateIDsGroups.filter(x => x[0].confirmed).length,
    });

    return summaryData;
  }

  renderUnclearHomeCountryTab() {
    const records = this.state.data.unclearHomeCountry;
    const pagedRecords = PagingControls.getPagedResults(records, this.state.unclearHomeCountryCurrentPage);
    return (
      records.length > 0 ? (
        <div>
          <p>
            Please confirm home country/location of employing entity for the work periods below.
            You can <a className="mintax-pointer">download</a> a spreadsheet to fill and{' '}
            <a className="mintax-pointer">upload back</a> if you prefer.
          </p>
          <table className="table table-bordered">
            <thead>
              <tr className="mintax-transparent-row">
                <td colSpan={7}>
                  <div className="mintax-left-right">
                    <span />
                    <PagingControls currentPage={this.state.unclearHomeCountryCurrentPage}
                                    total={records.length}
                                    onPageClick={newPage => this.setState({ unclearHomeCountryCurrentPage: newPage })} />
                  </div>
                </td>
              </tr>
              <tr>
                <th style={{ width: "50pt", minWidth: "50pt" }}>Ignore</th>
                <th style={{ width: "180pt", minWidth: "180pt" }}>Employee Name</th>
                <th style={{ width: "110pt", minWidth: "110pt" }}>Employee ID</th>
                <th style={{ width: "100pt", minWidth: "100pt" }}>Multiple Home Countries</th>
                <th style={{ width: "255pt", minWidth: "255pt" }}>Home Country</th>
                <th style={{ width: "105pt", minWidth: "105pt" }}>Date Effective From</th>
                <th style={{ width: "105pt", minWidth: "105pt" }}>
                  Date Effective To
                  {' '}
                  <span className="mintax-hint glyphicon glyphicon-info-sign"
                        title="Each employee's last entry can have this left blank if on-going." />
                </th>
                <th className="mintax-actions-column"></th>
              </tr>
            </thead>
            <tbody>
              {pagedRecords.map((emp, idx) => {
                const rowClasses = idx % 2 == 0 ? "mintax-striped-row" : "";
                const firstClarification = emp.clarifications[0];
                const rows = [];
                rows.push(
                  <tr key={`${emp.travellerName}-${emp.employeeId}-0`} className={rowClasses}>
                    <td className="mintax-checkbox-column" rowSpan={emp.clarifications.length}>
                      <input type="checkbox" checked={emp.ignore}
                             onChange={e => this.handleDataInputChange('ignore', emp, e)} />
                    </td>
                    <td rowSpan={emp.clarifications.length}>{emp.travellerName}</td>
                    <td rowSpan={emp.clarifications.length}>{emp.employeeId}</td>
                    <td className="mintax-checkbox-column" rowSpan={emp.clarifications.length}>
                      <input type="checkbox" checked={emp.clarifications.length > 1}
                             onChange={e => this.toggleChangeInMultipleHomeCountries(emp)} />
                    </td>
                    {this.renderUnclearHomeCountryCells(firstClarification, emp)}
                  </tr>
                );
                for (let idx = 1; idx < emp.clarifications.length; idx++) {
                  const clarification = emp.clarifications[idx];
                  rows.push(
                    <tr key={`${emp.travellerName}-${emp.employeeId}-${idx}`} className={rowClasses}>
                      {this.renderUnclearHomeCountryCells(clarification, emp)}
                    </tr>
                  );
                }
                return rows;
              })}
            </tbody>
            <tfoot>
              <tr className="mintax-transparent-row">
                <td colSpan={7}>
                    <PagingControls currentPage={this.state.unclearHomeCountryCurrentPage}
                                    total={records.length}
                                    onPageClick={newPage => this.setState({ unclearHomeCountryCurrentPage: newPage })} />
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      ) : (
        <p>No records found</p>
      )
    );
  }

  renderIncompleteTripsTab() {
    const filteredIncompleteTrips = this.getFilteredIncompleteTrips();
    const pagedRecords = PagingControls.getPagedResults(filteredIncompleteTrips, this.state.incompleteTripsCurrentPage);
    return (
        <div>
          <p>
            The following trips have incomplete or invalid data, being therefore ignored in the reports.
            Fix the issues to incorporate them in the results.
          </p>
          <div className="checkbox">
            <label>
              <input type="checkbox"
                     checked={this.state.showUKTouchingOnly}
                     onChange={this.handleShowUKTouchingOnlyChange} name="showUKTouchingOnly" />
              {' '}Show only UK touching trips
              ({this.state.data.incompleteTrips.length - filteredIncompleteTrips.length} currently hidden)
            </label>
          </div>
          {filteredIncompleteTrips.length > 0 ? (
            <table className="table table-bordered">
              <thead>
                <tr className="mintax-transparent-row">
                  <td colSpan={6}>
                    <div className="mintax-left-right">
                      <span />
                      <PagingControls currentPage={this.state.incompleteTripsCurrentPage}
                                      total={filteredIncompleteTrips.length}
                                      onPageClick={newPage => this.setState({ incompleteTripsCurrentPage: newPage })} />
                    </div>
                  </td>
                </tr>
                <tr>
                  <th style={{ width: "180pt", minWidth: "180pt" }}>Source Row</th>
                  <th style={{ width: "150pt", minWidth: "150pt" }}>Employee Name</th>
                  <th style={{ width: "110pt", minWidth: "110pt" }}>Employee ID</th>
                  <th style={{ width: "255pt", minWidth: "255pt" }}>Origin/Destination</th>
                  <th colSpan={2}>Departure/Arrival</th>
                  <th className="mintax-actions-column"></th>
                </tr>
              </thead>
              <tbody>
                {pagedRecords.map((trip, idx) => [
                  <tr key={`${trip.id}-first`} className={idx % 2 == 0 ? "mintax-striped-row" : ""}>
                    <td rowSpan={2}>{trip.sourceSpreadsheet}<br />Row #{trip.sourceRowNumber}</td>
                    <td rowSpan={2}>{trip.travellerName}</td>
                    <td rowSpan={2}>{trip.employeeId}</td>
                    <td>
                      <Select value={trip.originCountry}
                        onChange={selection => this.handleCountryChange(trip, 'originCountry', selection)}
                        isLoading={this.state.countries === undefined}
                        options={this.state.countries} />
                    </td>
                    <td className="mintax-datepicker-cell-fixer" style={{ width: "100pt", minWidth: "100pt" }}>
                      <DatePickerInput className="form-control"
                        selected={dates.parse(trip.departureDate)}
                        onChange={value => this.handleDateInputChange(value, trip, 'departureDate')}
                        onChangeRaw={event => this.handleDateInputChange(event, trip, 'departureDate')} />
                    </td>
                    <td style={{ width: "70pt", minWidth: "70pt" }}>
                      <TimeInput className="form-control" value={trip.departureTime} name="departureTime"
                                onChange={e => this.handleDataInputChange('departureTime', trip, e)} />
                    </td>
                    <td className="mintax-actions-column"></td>
                  </tr>,
                  <tr key={`${trip.id}-second`} className={idx % 2 == 0 ? "mintax-striped-row" : ""}>
                    <td>
                      <Select value={trip.destinationCountry}
                        onChange={selection => this.handleCountryChange(trip, 'destinationCountry', selection)}
                        isLoading={this.state.countries === undefined}
                        options={this.state.countries} />
                    </td>
                    <td className="mintax-datepicker-cell-fixer" style={{ width: "100pt", minWidth: "100pt" }}>
                      <DatePickerInput className="form-control"
                          selected={dates.parse(trip.arrivalDate)}
                          onChange={value => this.handleDateInputChange(value, trip, 'arrivalDate')}
                          onChangeRaw={event => this.handleDateInputChange(event, trip, 'arrivalDate')} />
                    </td>
                    <td style={{ width: "70pt", minWidth: "70pt" }}>
                      <TimeInput className="form-control" value={trip.arrivalTime} name="arrivalTime"
                                onChange={e => this.handleDataInputChange('arrivalTime', trip, e)} />
                    </td>
                    <td className="mintax-actions-column"></td>
                  </tr>
                ])}
              </tbody>
              <tfoot>
                <tr className="mintax-transparent-row">
                  <td colSpan={6}>
                    <PagingControls currentPage={this.state.incompleteTripsCurrentPage}
                                    total={filteredIncompleteTrips.length}
                                    onPageClick={newPage => this.setState({ incompleteTripsCurrentPage: newPage })} />
                  </td>
                </tr>
              </tfoot>
            </table>
          ) : (
            <p>No records found</p>
          )}
        </div>
    );
  }

  renderDuplicateIDsTab() {
    const duplicateIDGroups = this.getDuplicateIDGroups();
    var filteredDuplicateIDGroups = this.getFilteredDupĺicateIDGroups(duplicateIDGroups);
    var filteredDupShowUK = this.getFilteredDupShowUk(filteredDuplicateIDGroups);
    var pagedRecords = PagingControls.getPagedResults(filteredDuplicateIDGroups, this.state.duplicateIDsCurrentPage);
    pagedRecords = PagingControls.getPagedResults(filteredDupShowUK, this.state.duplicateIDsCurrentPage);
    return (
        <div>
          <p>
            The following employee groups share the same ID. Please confirm they are the same
            person or fix the issues in the traveller data spreadsheets.
          </p>
          <div className="checkbox  col-md-5">
            <label>
              <input type="checkbox"
                     checked={this.state.showUnansweredDuplicateIDsOnly}
                     onChange={this.handleUnansweredDuplicateIDsOnlyChange} name="showUnansweredDuplicateIDsOnly" />
              {' '}Show unanswered only
              ({duplicateIDGroups.length - filteredDuplicateIDGroups.length} groups currently hidden)
            </label>
            <label>
              <input type="checkbox"
                     checked={this.state.showDupUKTouchingOnly}
                     onChange={this.handleDuplicateShowUKTouchingOnlyChange} name="showDupUKTouchingOnly" />
              {' '}Show only UK touching trips
              ({duplicateIDGroups.length - filteredDupShowUK.length} groups currently hidden)
            </label>
          </div>
          {filteredDuplicateIDGroups.length > 0 ? (
            <table className="table table-bordered">
              <thead>
                <tr className="mintax-transparent-row">
                  <td colSpan={3}>
                    <div className="mintax-left-right">
                      <span />
                      <PagingControls currentPage={this.state.duplicateIDsCurrentPage}
                                      total={filteredDuplicateIDGroups.length}
                                      onPageClick={newPage => this.setState({ duplicateIDsCurrentPage: newPage })} />
                    </div>
                  </td>
                </tr>
                <tr>
                  <th style={{ width: "200pt", minWidth: "200pt" }}>Employee ID</th>
                  <th style={{ width: "200pt", minWidth: "200pt" }}>Employee Name</th>
                  <th style={{ width: "50pt", minWidth: "50pt" }}>Ignore</th>
                  <th style={{ width: "100pt", minWidth: "100pt" }} className="text-center">Same Person?</th>
                  <th className="mintax-actions-column"></th>
                </tr>
              </thead>
              <tbody>
                {pagedRecords.map((group, idx) => {
                  <p>{group[0].travellerName}</p>
                  const rows = [
                    <tr key={`${group[0].effectiveEmployeeId}-first`} className={idx % 2 == 0 ? "mintax-striped-row" : ""}>
                      <td rowSpan={group.length}>{group[0].effectiveEmployeeId}</td>
                      <td>{group[0].travellerName}</td>
                      <td className="mintax-checkbox-column">
                        <input type="checkbox" checked={group[0].ignore}
                              onChange={e => this.handleDataInputChange('ignore', group[0], e)} />
                      </td>
                      <td className="mintax-checkbox-column" rowSpan={group.length}>
                        <input type="checkbox" checked={group[0].confirmed}
                                onChange={e => this.toggleChangeInDuplicateIDConfirmation(e, group)} />
                      </td>
                      <td className="mintax-actions-column"></td>
                    </tr>
                  ];
                  for (let i = 1; i < group.length; i++) {
                    rows.push(
                      <tr key={`${group[i].effectiveEmployeeId}-${i}`} className={idx % 2 == 0 ? "mintax-striped-row" : ""}>
                        <td>{group[i].travellerName}</td>
                        <td className="mintax-checkbox-column">
                          <input type="checkbox" checked={group[i].ignore}
                                onChange={e => this.handleDataInputChange('ignore', group[i], e)} />
                        </td>
                        <td className="mintax-actions-column"></td>
                      </tr>
                    );
                  }
                  return rows;
                })}
              </tbody>
              <tfoot>
                <tr className="mintax-transparent-row">
                  <td colSpan={3}>
                    <PagingControls currentPage={this.state.duplicateIDsCurrentPage}
                                    total={filteredDuplicateIDGroups.length}
                                    onPageClick={newPage => this.setState({ duplicateIDsCurrentPage: newPage })} />
                  </td>
                </tr>
              </tfoot>
            </table>
          ) : (
            <p>No records found</p>
          )}
        </div>
    );
  }

  renderAssumedInboundTab() {
    const filteredInboundAssumptions = this.getFilteredInboundAssumptions();
    const pagedRecords = PagingControls.getPagedResults(filteredInboundAssumptions, this.state.assumedInboundCurrentPage);
    return (
      <div>
        <p>
          The following UK stays have their inbound date assumed. Please confirm the
          assumptions or provide the correct value as an override.
        </p>
        <div className="checkbox">
          <label>
            <input type="checkbox"
                   checked={this.state.showUnansweredInboundAssumptionsOnly}
                   onChange={this.handleUnansweredInboundAssumptionsOnlyChange} name="showUnansweredInboundAssumptionsOnly" />
            {' '}Show unanswered only
            ({this.state.data.inboundAssumptions.length - filteredInboundAssumptions.length} currently hidden)
          </label>
        </div>
        {filteredInboundAssumptions.length > 0 ? (
          <table className="table table-striped table-bordered">
            <thead>
              <tr className="mintax-transparent-row">
                <td colSpan={7}>
                  <div className="mintax-left-right">
                    <span />
                    <PagingControls currentPage={this.state.assumedInboundCurrentPage}
                                    total={filteredInboundAssumptions.length}
                                    onPageClick={newPage => this.setState({ assumedInboundCurrentPage: newPage })} />
                  </div>
                </td>
              </tr>
              <tr>
                <th style={{ width: "50pt", minWidth: "50pt" }}>Ignore</th>
                <th style={{ width: "180pt", minWidth: "180pt" }}>Source Row</th>
                <th style={{ width: "150pt", minWidth: "150pt" }}>Employee Name</th>
                <th style={{ width: "110pt", minWidth: "110pt" }}>Employee ID</th>
                <th style={{ width: "150pt", minWidth: "150pt" }}>Period</th>
                <th style={{ width: "90pt", minWidth: "90pt" }}>Confirm?</th>
                <th style={{ width: "105pt", minWidth: "105pt" }}>Correct Date</th>
              </tr>
            </thead>
            <tbody>
              {pagedRecords.map((trip, idx) => (
                <tr key={`${trip.travellerName}-${trip.employeeId}-${trip.fromDate}-${trip.toDate}`}>
                  <td className="mintax-checkbox-column">
                    <input type="checkbox" checked={trip.ignore}
                           onChange={e => this.handleDataInputChange('ignore', trip, e)} />
                  </td>
                  <td className="mintax-vmiddle">
                    {trip.sourceSpreadsheet ? (
                      <span>{trip.sourceSpreadsheet}<br />Row #{trip.sourceRowNumber}</span>
                    ) : (
                      <span>N/A</span>
                    )}
                  </td>
                  <td className="mintax-vmiddle">{trip.travellerName}</td>
                  <td className="mintax-vmiddle">{trip.employeeId}</td>
                  <td className="mintax-vmiddle">
                    <span className={trip.inboundAssumptionConfirmed === 'Y' ? "mintax-success" : "mintax-danger"}>
                      {dates.formatDate(trip.fromDate)}
                    </span>
                    {' '}-{' '}
                    {trip.toDate ? dates.formatDate(trip.toDate) : "current"}
                  </td>
                  <td className="mintax-vmiddle text-center">
                    <div className="radio-inline">
                      <label>
                        <input type="radio" name={`${trip.travellerName}-${trip.employeeId}-${trip.fromDate}-${trip.toDate}-inbound-assumption-confirmed`}
                               checked={trip.inboundAssumptionConfirmed === 'Y'}
                               onChange={e => this.handleDataInputChange('inboundAssumptionConfirmed', trip, e)} value="Y" />
                        {' '}Yes
                      </label>
                    </div>
                    <div className="radio-inline">
                      <label>
                        <input type="radio" name={`${trip.travellerName}-${trip.employeeId}-${trip.fromDate}-${trip.toDate}-inbound-assumption-confirmed`}
                              checked={trip.inboundAssumptionConfirmed === 'N'}
                              onChange={e => this.handleDataInputChange('inboundAssumptionConfirmed', trip, e)} value="N" />
                        {' '}No
                      </label>
                    </div>
                  </td>
                  <td className="mintax-datepicker-cell-fixer" style={{ width: "100pt", minWidth: "100pt" }}>
                    <DatePickerInput className="form-control"
                                     selected={dates.parse(trip.correctFromDate)}
                                     disabled={trip.inboundAssumptionConfirmed !== 'N'}
                                     onChange={value => this.handleDateInputChange(value, trip, 'correctFromDate')}
                                     onChangeRaw={event => this.handleDateInputChange(event, trip, 'correctFromDate')} />
                  </td>
                  <td className="mintax-actions-column"></td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="mintax-transparent-row">
                <td colSpan={7}>
                  <PagingControls currentPage={this.state.assumedInboundCurrentPage}
                                  total={filteredInboundAssumptions.length}
                                  onPageClick={newPage => this.setState({ assumedInboundCurrentPage: newPage })} />
                </td>
              </tr>
            </tfoot>
          </table>
        ) : (
          <p>No records found</p>
        )}
      </div>
    );
  }
  
  renderAssumedOutboundTab() {
    const filteredOutboundAssumptions = this.getFilteredOutboundAssumptions();
    const pagedRecords = PagingControls.getPagedResults(filteredOutboundAssumptions, this.state.assumedOutboundCurrentPage);
    return (
      <div>
        <p>
          The following UK stays have their outbound date assumed. Please confirm the
          assumptions or provide the correct value as an override.
        </p>
        <div className="checkbox">
          <label>
            <input type="checkbox"
                    checked={this.state.showUnansweredOutboundAssumptionsOnly}
                    onChange={this.handleUnansweredOutboundAssumptionsOnlyChange} name="showUnansweredOutboundAssumptionsOnly" />
            {' '}Show unanswered only
            ({this.state.data.outboundAssumptions.length - filteredOutboundAssumptions.length} currently hidden)
          </label>
        </div>
        {filteredOutboundAssumptions.length > 0 ? (
          <table className="table table-striped table-bordered">
            <thead>
              <tr className="mintax-transparent-row">
                <td colSpan={7}>
                  <div className="mintax-left-right">
                    <span />
                    <PagingControls currentPage={this.state.assumedOutboundCurrentPage}
                                    total={filteredOutboundAssumptions.length}
                                    onPageClick={newPage => this.setState({ assumedOutboundCurrentPage: newPage })} />
                  </div>
                </td>
              </tr>
              <tr>
                <th style={{ width: "50pt", minWidth: "50pt" }}>Ignore</th>
                <th style={{ width: "180pt", minWidth: "180pt" }}>Source Row</th>
                <th style={{ width: "150pt", minWidth: "150pt" }}>Employee Name</th>
                <th style={{ width: "110pt", minWidth: "110pt" }}>Employee ID</th>
                <th style={{ width: "150pt", minWidth: "150pt" }}>Period</th>
                <th style={{ width: "90pt", minWidth: "90pt" }}>Confirm?</th>
                <th style={{ width: "105pt", minWidth: "105pt" }}>Correct Date</th>
              </tr>
            </thead>
            <tbody>
              {pagedRecords.map((trip, idx) => (
                <tr key={`${trip.travellerName}-${trip.employeeId}-${trip.fromDate}-${trip.toDate}`}>
                  <td className="mintax-checkbox-column">
                    <input type="checkbox" checked={trip.ignore}
                          onChange={e => this.handleDataInputChange('ignore', trip, e)} />
                  </td>
                  <td className="mintax-vmiddle">
                    {trip.sourceSpreadsheet ? (
                      <span>{trip.sourceSpreadsheet}<br />Row #{trip.sourceRowNumber}</span>
                    ) : (
                      <span>N/A</span>
                    )}
                  </td>
                  <td className="mintax-vmiddle">{trip.travellerName}</td>
                  <td className="mintax-vmiddle">{trip.employeeId}</td>
                  <td className="mintax-vmiddle">
                    {dates.formatDate(trip.fromDate)}
                    {' '}-{' '}
                    <span className={trip.outboundAssumptionConfirmed === 'Y' ? "mintax-success" : "mintax-danger"}>
                      {trip.toDate ? dates.formatDate(trip.toDate) : "current"}
                    </span>
                  </td>
                  <td className="mintax-vmiddle text-center">
                    <div className="radio-inline">
                      <label>
                        <input type="radio" name={`${trip.travellerName}-${trip.employeeId}-${trip.fromDate}-${trip.toDate}-outbound-assumption-confirmed`}
                                checked={trip.outboundAssumptionConfirmed === 'Y'}
                                onChange={e => this.handleDataInputChange('outboundAssumptionConfirmed', trip, e)} value="Y" />
                        {' '}Yes
                      </label>
                    </div>
                    <div className="radio-inline">
                      <label>
                        <input type="radio" name={`${trip.travellerName}-${trip.employeeId}-${trip.fromDate}-${trip.toDate}-outbound-assumption-confirmed`}
                              checked={trip.outboundAssumptionConfirmed === 'N'}
                              onChange={e => this.handleDataInputChange('outboundAssumptionConfirmed', trip, e)} value="N" />
                        {' '}No
                      </label>
                    </div>
                  </td>
                  <td className="mintax-datepicker-cell-fixer" style={{ width: "100pt", minWidth: "100pt" }}>
                    <DatePickerInput className="form-control"
                                      selected={dates.parse(trip.correctToDate)}
                                      disabled={trip.outboundAssumptionConfirmed !== 'N'}
                                      onChange={value => this.handleDateInputChange(value, trip, 'correctToDate')}
                                      onChangeRaw={event => this.handleDateInputChange(event, trip, 'correctToDate')} />
                  </td>
                  <td className="mintax-actions-column"></td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="mintax-transparent-row">
                <td colSpan={7}>
                  <PagingControls currentPage={this.state.assumedOutboundCurrentPage}
                                  total={filteredOutboundAssumptions.length}
                                  onPageClick={newPage => this.setState({ assumedOutboundCurrentPage: newPage })} />
                </td>
              </tr>
            </tfoot>
          </table>
        ) : (
          <p>No records found</p>
        )}
      </div>
    );
  }

  renderUnclearBorderCrossTimeTrip(trip) {
    return [
      <td className="text-center mintax-vmiddle" key="origin">{trip.originCountry}</td>,
      <td className="text-center mintax-vmiddle" key="destination">{trip.destinationCountry}</td>,
      <td key="correct-time">
        <TimeInput className="form-control" value={trip.correctTime} name="correctTime"
                   onChange={e => this.handleDataInputChange('correctTime', trip, e)} />
      </td>,
      <td key="source-row">{trip.sourceSpreadsheet}<br />Row #{trip.sourceRowNumber}</td>
    ];
  }

  renderUnclearBorderCrossTimeTab() {
    const tripGroups = this.getUnclearBorderCrossTimeGroups()
    const filteredTripGroups = this.getFilteredUnclearBorderCrossTimeGroups(tripGroups);
    const pagedRecords = PagingControls.getPagedResults(filteredTripGroups, this.state.unclearBorderCrossCurrentPage);
    return (
      <div>
        <p>
          The following UK touching trips have their chronological order unclear.
          Please provide accurate time information for each group in order to fix this.
        </p>
        <div className="checkbox">
          <label>
            <input type="checkbox"
                   checked={this.state.showUnansweredUnclearBorderCrossOnly}
                   onChange={this.handleUnansweredUnclearBorderCrossChange} name="showUnansweredUnclearBorderCrossOnly" />
            {' '}Show unanswered only
            ({tripGroups.length - filteredTripGroups.length} currently hidden)
          </label>
        </div>
        {filteredTripGroups.length > 0 ? (
          <table className="table table-bordered">
            <thead>
              <tr className="mintax-transparent-row">
                <td colSpan={8}>
                  <div className="mintax-left-right">
                    <span />
                    <PagingControls currentPage={this.state.unclearBorderCrossCurrentPage}
                                    total={filteredTripGroups.length}
                                    onPageClick={newPage => this.setState({ unclearBorderCrossCurrentPage: newPage })} />
                  </div>
                </td>
              </tr>
              <tr>
                <th style={{ width: "50pt", minWidth: "50pt" }} rowSpan={2}>Ignore</th>
                <th style={{ width: "150pt", minWidth: "150pt" }} rowSpan={2}>Employee Name</th>
                <th style={{ width: "110pt", minWidth: "110pt" }} rowSpan={2}>Employee ID</th>
                <th style={{ width: "150pt", minWidth: "150pt" }} rowSpan={2}>UK Border Cross Date</th>
                <th colSpan={4} className="text-center">Conflicting Trips</th>
                <th rowSpan={2} className="mintax-actions-column" />
              </tr>
              <tr>
                <th className="text-center" style={{ width: "80pt", minWidth: "80pt" }}>Origin</th>
                <th className="text-center" style={{ width: "80pt", minWidth: "80pt" }}>Destination</th>
                <th className="text-center" style={{ width: "100pt", minWidth: "100pt" }}>Correct Time</th>
                <th style={{ width: "200pt", minWidth: "200pt" }}>Source Row</th>
              </tr>
            </thead>
            <tbody>
              {pagedRecords.map((tripGroup, idx) => {
                let trip  = tripGroup[0];
                const rows = [(
                  <tr key={`${tripGroup.travellerName}-${tripGroup.employeeId}-${tripGroup.borderCross}-0`}
                      className={idx % 2 == 0 ? "mintax-striped-row" : ""}>
                    <td className="mintax-checkbox-column" rowSpan={tripGroup.length}>
                      <input type="checkbox" checked={tripGroup[0].ignore}
                              onChange={e => this.toggleIgnoreBorderCrossTrips(tripGroup)} />
                    </td>
                    <td className="mintax-vmiddle" rowSpan={tripGroup.length}>{trip.travellerName}</td>
                    <td className="mintax-vmiddle" rowSpan={tripGroup.length}>{trip.employeeId}</td>
                    <td className="mintax-vmiddle" rowSpan={tripGroup.length}>{dates.formatDateTime(trip.borderCross)}</td>
                    {this.renderUnclearBorderCrossTimeTrip(trip)}
                    <td rowSpan={tripGroup.length} className="mintax-actions-column"></td>
                  </tr>
                )];
                for (let tripIdx = 1; tripIdx < tripGroup.length; tripIdx++) {
                  trip = tripGroup[tripIdx];
                  rows.push((
                    <tr key={`${tripGroup.travellerName}-${tripGroup.employeeId}-${tripGroup.borderCross}-${tripIdx}`}
                        className={idx % 2 == 0 ? "mintax-striped-row" : ""}>
                      {this.renderUnclearBorderCrossTimeTrip(trip)}
                    </tr>
                  ));
                }
                return rows;
              })}
            </tbody>
            <tfoot>
              <tr className="mintax-transparent-row">
                <td colSpan={8}>
                  <PagingControls currentPage={this.state.unclearBorderCrossCurrentPage}
                                  total={filteredTripGroups.length}
                                  onPageClick={newPage => this.setState({ unclearBorderCrossCurrentPage: newPage })} />
                </td>
              </tr>
            </tfoot>
          </table>
        ) : (
          <p>No records found</p>
        )}
      </div>
    );
  }

  renderIgnoredEmployeesTab() {
    const ignoredEmployees = this.state.data.ignoredEmployees;
    const pagedRecords = PagingControls.getPagedResults(ignoredEmployees, this.state.ignoredEmployeesCurrentPage);
    return (
        <div>
          <p>
            The following employees have been ignored and are not counting towards any report results.
          </p>
          {ignoredEmployees.length > 0 ? (
            <table className="table table-bordered table-striped">
              <thead>
                <tr className="mintax-transparent-row">
                  <td colSpan={3}>
                    <div className="mintax-left-right">
                      <span />
                      <PagingControls currentPage={this.state.ignoredEmployeesCurrentPage}
                                      total={ignoredEmployees.length}
                                      onPageClick={newPage => this.setState({ ignoredEmployeesCurrentPage: newPage })} />
                    </div>
                  </td>
                </tr>
                <tr>
                  <th style={{ width: "200pt", minWidth: "200pt" }}>Employee ID</th>
                  <th style={{ width: "200pt", minWidth: "200pt" }}>Employee Name</th>
                  <th style={{ width: "100pt", minWidth: "100pt" }} className="text-center">Undo Ignore</th>
                  <th className="mintax-actions-column"></th>
                </tr>
              </thead>
              <tbody>
                {pagedRecords.map(employee => (
                  <tr key={employee.id}>
                    <td>{employee.employeeId}</td>
                    <td>{employee.travellerName}</td>
                    <td className="mintax-checkbox-column">
                      <input type="checkbox" checked={employee.undoIgnore}
                              onChange={e => this.handleDataInputChange('undoIgnore', employee, e)} />
                    </td>
                    <td className="mintax-actions-column"></td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="mintax-transparent-row">
                  <td colSpan={3}>
                    <PagingControls currentPage={this.state.ignoredEmployeesCurrentPage}
                                    total={ignoredEmployees.length}
                                    onPageClick={newPage => this.setState({ ignoredEmployeesCurrentPage: newPage })} />
                  </td>
                </tr>
              </tfoot>
            </table>
          ) : (
            <p>No records found</p>
          )}
        </div>
    );
  }

  renderIgnoredTripsTab() {
    const ignoredTrips = this.state.data.ignoredTrips;
    const pagedRecords = PagingControls.getPagedResults(ignoredTrips, this.state.ignoredTripsCurrentPage);
    return (
        <div>
          <p>
            The following trips have been ignored and are not counting towards any report results.
          </p>
          {ignoredTrips.length > 0 ? (
            <table className="table table-bordered table-striped">
              <thead>
                <tr className="mintax-transparent-row">
                  <td colSpan={7}>
                    <div className="mintax-left-right">
                      <span />
                      <PagingControls currentPage={this.state.ignoredTripsCurrentPage}
                                      total={ignoredTrips.length}
                                      onPageClick={newPage => this.setState({ ignoredTripsCurrentPage: newPage })} />
                    </div>
                  </td>
                </tr>
                <tr>
                  <th style={{ width: "125pt", minWidth: "125pt" }}>Employee ID</th>
                  <th style={{ width: "125pt", minWidth: "125pt" }}>Employee Name</th>
                  <th style={{ width: "80pt", minWidth: "80pt" }}>Origin</th>
                  <th style={{ width: "80pt", minWidth: "80pt" }}>Destination</th>
                  <th style={{ width: "100pt", minWidth: "100pt" }}>Departure</th>
                  <th style={{ width: "100pt", minWidth: "100pt" }}>Arrival</th>
                  <th style={{ width: "100pt", minWidth: "100pt" }} className="text-center">Undo Ignore</th>
                  <th className="mintax-actions-column"></th>
                </tr>
              </thead>
              <tbody>
                {pagedRecords.map(trip => (
                  <tr key={trip.id}>
                    <td>{trip.employeeId}</td>
                    <td>{trip.travellerName}</td>
                    <td>{trip.origin}</td>
                    <td>{trip.destination}</td>
                    <td>{trip.departureDate}{trip.departureTime ? ` ${trip.departureTime}` : ''}</td>
                    <td>{trip.arrivalDate}{trip.arrivalTime ? ` ${trip.arrivalTime}` : ''}</td>
                    <td className="mintax-checkbox-column">
                      <input type="checkbox" checked={trip.undoIgnore}
                              onChange={e => this.handleDataInputChange('undoIgnore', trip, e)} />
                    </td>
                    <td className="mintax-actions-column"></td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="mintax-transparent-row">
                  <td colSpan={7}>
                    <PagingControls currentPage={this.state.ignoredTripsCurrentPage}
                                    total={ignoredTrips.length}
                                    onPageClick={newPage => this.setState({ ignoredTripsCurrentPage: newPage })} />
                  </td>
                </tr>
              </tfoot>
            </table>
          ) : (
            <p>No records found</p>
          )}
        </div>
    );
  }

  renderTabContent() {
    switch (this.state.activeTab) {
      case 'summary': return this.renderSummaryTab();
      case 'unclear-home-country': return this.renderUnclearHomeCountryTab();
      case 'incomplete-trips': return this.renderIncompleteTripsTab();
      case 'assumed-inbound': return this.renderAssumedInboundTab();
      case 'assumed-outbound': return this.renderAssumedOutboundTab();
      case 'unclear-border-cross-time': return this.renderUnclearBorderCrossTimeTab();
      case 'duplicate-ids': return this.renderDuplicateIDsTab();
      case 'ignored-employees': return this.renderIgnoredEmployeesTab();
      case 'ignored-trips': return this.renderIgnoredTripsTab();
      default: return <p>Unknown tab!</p>
    }
  }

  render() {

    if (this.state.data === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data === null) {
      return <AjaxError />
    }

    return (
      <form className="mintax-form" onSubmit={this.send}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="row">
              <div className="col-xs-12 col-sm-3 col-lg-2">
                <ul className="nav nav-pills nav-stacked noselect">
                  <li className={this.state.activeTab == 'summary' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'summary' })}>Summary</a>
                  </li>
                  <li className={this.state.activeTab == 'unclear-home-country' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'unclear-home-country' })}>Unclear Home Country</a>
                  </li>
                  <li className={this.state.activeTab == 'incomplete-trips' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'incomplete-trips' })}>Incomplete Trips</a>
                  </li>
                  <li className={this.state.activeTab == 'assumed-inbound' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'assumed-inbound' })}>Assumed Inbound Trips</a>
                  </li>
                  <li className={this.state.activeTab == 'assumed-outbound' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'assumed-outbound' })}>Assumed Outbound Trips</a>
                  </li>
                  <li className={this.state.activeTab == 'unclear-border-cross-time' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'unclear-border-cross-time' })}>Unclear Border Cross Time</a>
                  </li>
                  <li className={this.state.activeTab == 'duplicate-ids' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'duplicate-ids' })}>Duplicate IDs</a>
                  </li>
                  <li className={this.state.activeTab == 'ignored-employees' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'ignored-employees' })}>Ignored Employees</a>
                  </li>
                  <li className={this.state.activeTab == 'ignored-trips' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'ignored-trips' })}>Ignored Trips</a>
                  </li>
                </ul>
              </div>
              <div className="col-xs-12 col-sm-9 col-lg-10">
                {this.renderTabContent()}
              </div>
            </div>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group-right">
            <button className="btn btn-primary"
                    disabled={!this.hasPendingChanges()}
                    title={!this.hasPendingChanges() ? "There is no unsaved changes" : ""}>Save</button>
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
        <UnsavedDataHandler verifier={() => this.hasPendingChanges()} />
      </form>
    );
  }
}

export default AdditionalClarifications;