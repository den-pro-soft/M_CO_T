import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import moment from 'moment';
import ajax from '../shared/ajax';
import msgbox from '../shared/msgbox';
import handleInputChange from '../shared/handleInputChange';
import dates from '../shared/dates';
import DatePickerInput from './DatePickerInput';
import Scrollbars from './Scrollbars';
import AjaxError from './AjaxError';


const GROUPS = [1, 31, 60, 91, 151, 184];

const POS_UK = 1;
const POS_UNKNOWN = 2;
const POS_TREATY = 3;
const POS_NON_TREATY = 4;
const POS_BRANCH = 5;
const POS_EXPAT = 6;
const ALL_POSITIONS = [POS_UK, POS_EXPAT, POS_BRANCH, POS_NON_TREATY, POS_TREATY, POS_UNKNOWN];


const POSITION_CONFIGS = {
  "1": {
    title: "UK Employees",
    classNames: {
      withSPR: ["", "", "", "", "", ""],
      withoutSPR: ["", "", "", "", "", ""],
    },
    showClarifications: false,
  },
  "3": {
    title: "Treaty Country",
    classNames: {
      withSPR: ["mintax-success", "mintax-success", "mintax-warning", "mintax-warning", "mintax-warning", "mintax-danger"],
      withoutSPR: ["mintax-success", "mintax-success", "mintax-warning", "mintax-warning", "mintax-warning", "mintax-danger"],
    },
    showClarifications: false,
  },
  "4": {
    title: "Non-Treaty Country",
    classNames: {
      withSPR: ["mintax-success", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger"],
      withoutSPR: ["mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger"],
    },
    showClarifications: false,
  },
  "5": {
    title: "Branch Visitors",
    classNames: {
      withSPR: ["mintax-success", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger"],
      withoutSPR: ["mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger"],
    },
    showClarifications: false,
  },
  "6": {
    title: "UK Expatriates",
    classNames: {
      withSPR: ["", "", "", "", "", ""],
      withoutSPR: ["", "", "", "", "", ""],
    },
    showClarifications: false,
  },
  "2": {
    title: "Unknowns",
    classNames: {
      withSPR: ["mintax-success", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger"],
      withoutSPR: ["mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger", "mintax-danger"],
    },
    showClarifications: true,
  },
};


const identifyWorkdaysGroup = function (days) {
  for (const idx in GROUPS) {
    const group = GROUPS[idx];
    const lastGroup = idx == GROUPS.length - 1;
    if (group <= days && (lastGroup || GROUPS[parseInt(idx) + 1] > days)) {
      return idx;
    }
  }
  throw Error('Should not get here never (' + days + ')');
};


class ReportResults extends Component {
  constructor(props) {
    super(props);
    this.state = {

      fetching: true,

      periods: {
        1: { from: undefined, to: undefined, stays: undefined },
        2: { from: undefined, to: undefined, stays: undefined },
        3: { from: undefined, to: undefined, stays: undefined },
        4: { from: undefined, to: undefined, stays: undefined },
        5: { from: undefined, to: undefined, stays: undefined }, // one for each treaty position
      },

      // are we viewing the employee table?
      viewingEmployees: false,

      employeesParameters: {
        positions: [], // which work arrangements? e.g. treaty country and overseas branch
        workdaysGroup: null, // which workdays group? e.g. 60-90
      },

      employeesTextFilter: "", // allowing custom user filter

      ignoredEmployees: [], // tuples marked to be ignored
    };
    this.fetchData = this.fetchData.bind(this);
    this.viewEmployees = this.viewEmployees.bind(this);
    this.handlePeriodSelectionChange = this.handlePeriodSelectionChange.bind(this);
    this.handleInputChange = handleInputChange.bind(this);
  }

  ignoreEmployees() {
    const data = this.state.ignoredEmployees;
    ajax.exec('employees/ignored', 'POST', data, event.target).then(() => {
      msgbox.alert("The selected employees have been successfully ignored").then(() => {
        this.state.ignoredEmployees = [];
        this.fetchData();
      });
    });
  }

  toggleEmployeeIgnore(employee) {
    const ignoredEmployees = this.state.ignoredEmployees;
    let index = this.findIndexOfIgnoredEmployee(employee);
    if (index === -1) {
      ignoredEmployees.push({
        travellerName: employee.travellerName,
        employeeId: employee.employeeId,
      });
    } else {
      ignoredEmployees.splice(index, 1);
    }
    this.setState({ ignoredEmployees });
  }

  isEmployeeIgnored(employee) {
    return this.findIndexOfIgnoredEmployee(employee) !== -1;
  }

  findIndexOfIgnoredEmployee(employee) {
    const ignoredEmployees = this.state.ignoredEmployees;
    for (let i = 0; i < ignoredEmployees.length; i++) {
      if (ignoredEmployees[i].travellerName == employee.travellerName &&
          ignoredEmployees[i].employeeId == employee.employeeId) {
        return i;
      }
    }
    return -1;
  }

  handlePeriodSelectionChange(eventOrValue, position, fieldName) {
    const periods = this.state.periods;
    position[fieldName] = eventOrValue && eventOrValue.target ? eventOrValue.target.value : eventOrValue;;
    const from = dates.parse(position.fromSelection);
    const to = dates.parse(position.toSelection);
    position.invalid = from && to && to.isBefore(from);
    this.setState({ periods });
  }

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    if (this.eventSourceCloseHandler) {
      this.eventSourceCloseHandler();
    }
  }

  getQuery(positions) {
    if (positions.length == 1) {
      const position = positions[0];
      const periods = this.state.periods;
      const fromDate = periods[position].fromSelection;
      const toDate = periods[position].toSelection;
      const categories = positions;
      return { fromDate, toDate, categories };
    } else {
      return {
        fromDate: null,
        toDate: null,
        categories: positions,
      };
    }
  }

  fetchData(position) {

    if (position) {
      const periods = this.state.periods;
      periods[position].stays = undefined;
      this.setState({ periods });
    }

    const positions = position ? [position] : ALL_POSITIONS;
    const query = this.getQuery(positions);
    ajax.exec('report-results', 'POST', query)
      .then(rawData => {

        // listen for server-sent events if processing traveller data
        if (this.eventSourceCloseHandler) {
          this.eventSourceCloseHandler();
        }
        if (rawData.progressEventChannel) {
          this.eventSourceCloseHandler = ajax.subscribe(rawData.progressEventChannel, processingProgress => {
            if (processingProgress && processingProgress.progress === 100) {
              this.fetchData();
            } else {
              this.setState({ processingProgress });
            }
          });
        }

        const periods = this.state.periods;

        positions.forEach(position => {
          const results = rawData.resultsPerCategory[position];
          const aggregator = {};
          periods[position] = {
            to: results.toDate,
            from: results.fromDate,
            toSelection: results.toDate,
            fromSelection: results.fromDate,
            stays: aggregator,
          };
          results.stays.forEach(stay => {
            const aggregationId = `${stay.travellerName}-${stay.employeeId}`;
            if (!aggregator[aggregationId]) {
              aggregator[aggregationId] = {
                travellerName: stay.travellerName,
                employeeId: stay.employeeId,
                days: stay.days,
              };
            } else {
              aggregator[aggregationId].days += stay.days;
            }
          });
        });

        this.setState({
          periods,
          lastRequest: rawData.lastRequest,
          availableData: rawData.availableData,
          lastError: rawData.lastError,
          simplifiedPayroll: rawData.simplifiedPayroll,
          fetching: false,
        });

      }, () => {
        
        // enter error state if it is the first query
        // and not a refresh
        const periods = this.state.periods;
        positions.forEach(position => {
          periods[position].stays = null;
        });
        this.setState({ periods, fetching: false });

      });
  }

  viewEmployees(positions, workdaysGroup) {
    this.setState({
      viewingEmployees: true,
      employeesParameters: { positions, workdaysGroup },
    });
  }

  renderSign() {

    if (this.state.fetching) {
      return <span />;
    }

    if (!this.state.lastRequest) {
      return (
        <span className="mintax-sign-info">
          <span className="glyphicon glyphicon-exclamation-sign" />
          <span className="mintax-sign-caption">No data uploaded yet</span>
        </span>
      )
    } else if (this.state.lastRequest === this.state.lastError) {
      return (
        <span className="mintax-sign-error">
          <span className="glyphicon glyphicon-exclamation-sign" />
          <span className="mintax-sign-caption">An error ocurred, please send an e-mail to contactus@e-taxconsulting.com</span>
        </span>
      )
    } else if (this.state.lastRequest !== this.state.availableData) {
      return (
        <span className="mintax-sign-alert">
          <span className="glyphicon glyphicon-exclamation-sign" />
          <span className="mintax-sign-caption">
            {this.state.processingProgress ? (
              <span>
                {this.state.processingProgress.status} ({this.state.processingProgress.progress}%).
                Please wait, the page will update automatically.
              </span>
            ) : (
              <span>
                Processing... Please wait, the page will update automatically. Taking too long?
                Please try refreshing the page.
              </span>
            )}
          </span>
        </span>
      )
    } else {
      return (
        <span className="mintax-sign-success">
          <span className="glyphicon glyphicon-ok" />
          <span className="mintax-sign-caption">Results are up-to-date</span>
        </span>
      )
    }
  }

  getEmployees(positions) {

    const periods = this.state.periods;

    // key is aggregationId, value is an object with traveller name, id and workdays
    const employees = {};
    positions.forEach(position => {
      if (periods[position].stays) {
        for (const aggregationId in periods[position].stays) {
          const employee = periods[position].stays[aggregationId];
          if (!employees[aggregationId]) {
            employees[aggregationId] = {
              travellerName: employee.travellerName,
              employeeId: employee.employeeId,
              days: 0,
            };
          }
          employees[aggregationId].days += employee.days;
        }
      }
    });

    for (const aggregationId in employees) {
      const employee = employees[aggregationId];
      employee.workdaysGroup = identifyWorkdaysGroup(employee.days);
    }

    return Object.values(employees);
  }

  renderEmployeeCounts(positions) {
    
    const positionConfig = positions.length == 1 ?
      POSITION_CONFIGS[positions[0]] : undefined;

    const periods = this.state.periods;
    let fetching = false;
    if (positions.length == 1) {
      fetching = periods[positions[0]].stays === undefined;
    } else {
      ALL_POSITIONS.forEach(position => {
        if (periods[position].stays === undefined) {
          fetching = true;
        }
      })
    }
    if (fetching) {
      return <td colSpan={7} className="mintax-ajax-in-progress" />;
    }

    // cell highlight colour
    const hasSimplifiedPayroll = this.state.simplifiedPayroll;
    const classNamesKey = hasSimplifiedPayroll ? "withSPR" : "withoutSPR";
    const classNames = positionConfig ? positionConfig.classNames[classNamesKey] : undefined;

    let total = 0; // sum of all workday groups
    const totals = [];
    GROUPS.forEach(group => totals.push(0));

    const employees = this.getEmployees(positions);
    employees.forEach(employee => {
      total++;
      totals[employee.workdaysGroup]++;
    });

    let cells = [];
    
    cells.push(total > 0 ?
      <td className="text-center mintax-pointer mintax-underline" key="total"
          onClick={() => this.viewEmployees(positions, null)}>{total}</td> :
      <td className="text-center" key="total">-</td>
    );

    // we don't show workdays group-based totals
    if (positionConfig) {
      cells = cells.concat(GROUPS.map((group, idx) => (
                            totals[idx] == 0 ? (
                              <td key={group} className="text-center">-</td>
                            ) : (
                              <td key={group} className={`text-center mintax-pointer mintax-underline ${classNames ? classNames[idx] : ""}`}
                                  onClick={() => this.viewEmployees(positions, idx)}>{totals[idx]}</td>
                            )
                          )));
    }

    return cells;
  }

  isDirtyPeriod(position) {
    const periods = this.state.periods;
    return !_.isEqual(periods[position].from, periods[position].fromSelection) ||
           !_.isEqual(periods[position].to, periods[position].toSelection);
  }

  renderTable() {

    if (this.state.fetching) {
      return <p className="mintax-ajax-in-progress" />;
    }

    const periods = this.state.periods;

    const rows = ALL_POSITIONS.map(position =>
      <tr key={position}>
        <td className={`mintax-datepicker-cell-fixer mintax-condensed-date-picker-cell mintax-vtop ${periods[position].invalid ? "mintax-invalid-cell" : ""}`}>
          <DatePickerInput className="form-control"
              selected={dates.parse(periods[position].fromSelection)}
              onChange={value => this.handlePeriodSelectionChange(value, periods[position], 'fromSelection')}
              onChangeRaw={event => this.handlePeriodSelectionChange(event, periods[position], 'fromSelection')} />
        </td>
        <td className={`mintax-datepicker-cell-fixer mintax-condensed-date-picker-cell mintax-vtop ${periods[position].invalid ? "mintax-invalid-cell" : ""}`}>
          <DatePickerInput className="form-control"
              selected={dates.parse(periods[position].toSelection)}
              onChange={value => this.handlePeriodSelectionChange(value, periods[position], 'toSelection')}
              onChangeRaw={event => this.handlePeriodSelectionChange(event, periods[position], 'toSelection')} />
        </td>
        <td>
          {POSITION_CONFIGS[position].title}
          {'  '}
          {POSITION_CONFIGS[position].showClarifications ? (
            <span> - <Link to="/clarifications"><i className="glyphicon glyphicon-share"/> Clarifications</Link></span>
          ) : <span />}
        </td>
        {this.renderEmployeeCounts([ position ])}
        <td className="text-center">
          <a className={`mintax-action-link mintax-yellow ${this.isDirtyPeriod(position) ? 'mintax-warning' : ''}`}
             title="Click to reload this row using the selected report period"
             disabled={periods[position].invalid}
             onClick={() => this.fetchData(position)}>
            <i className="glyphicon glyphicon-pencil" />
          </a>
          {' '}
          <a className="mintax-action-link" title="Download">
            <i className="glyphicon glyphicon-download-alt" />
          </a>
        </td>
        <td className="mintax-actions-column">
        </td>
      </tr>
    );
    rows.push(
      <tr className="mintax-totalizer-row" key="total">
          <td className="mintax-actions-column" />
          <td className="mintax-actions-column" />
          <td>Total</td>
          {this.renderEmployeeCounts(ALL_POSITIONS)}
      </tr>
    );

    let atLeastOneInvalid = Object.values(periods).filter(period => period.invalid).length > 0;
    
    return (
      <div>
        <table className="table table-striped table-bordered table-condensed mintax-table-vmiddle mintax-margin-bottom">
          <thead>
            <tr>
              <th colSpan={2} className="text-center">Report Period</th>
              <th rowSpan={2} style={{ width: "150pt", minWidth: "150pt" }}>Treaty Position</th>
              <th rowSpan={2} className="text-center" style={{ width: "70pt", minWidth: "70pt" }}>Total Travellers</th>
              <th colSpan={6} className="text-center">Day Count</th>
              <th rowSpan={2} style={{ width: "48pt", minWidth: "48pt" }} className="text-center">Actions</th>
              <th rowSpan={2} className="mintax-actions-column">
              </th>
            </tr>
            <tr>
              <th className="text-center" style={{ width: "98pt", minWidth: "98pt" }}>Date From</th>
              <th className="text-center" style={{ width: "98pt", minWidth: "98pt" }}>
                Date To
                {' '}
                {atLeastOneInvalid ? (
                  <span className="mintax-danger glyphicon glyphicon-ban-circle"
                        title="To date must be equal or after From date" />
                ) : <span />}
              </th>
              <th className="text-center" style={{ width: "58pt", minWidth: "58pt" }}>30 or less</th>
              <th className="text-center" style={{ width: "58pt", minWidth: "58pt" }}>31-59</th>
              <th className="text-center" style={{ width: "58pt", minWidth: "58pt" }}>60-90</th>
              <th className="text-center" style={{ width: "58pt", minWidth: "58pt" }}>91-150</th>
              <th className="text-center" style={{ width: "58pt", minWidth: "58pt" }}>151-183</th>
              <th className="text-center" style={{ width: "58pt", minWidth: "58pt" }}>184 plus</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    );
  }

  renderReport() {
    return (
      <div className="mintax-form">
        <Scrollbars>
          <div className="mintax-form-body">
            <p>{this.renderSign()}</p>
            <p className="mintax-form-hint">  
              <span className="glyphicon glyphicon-info-sign" />{' '}
              Click a number to view the employee list
            </p>
            {this.renderTable()}
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group">
            <span className="mintax-ajax-indicator" />
          </div>
          <div className="mintax-button-group">
            <button className="btn btn-warning"
                    onClick={() => this.ignoreEmployees()}
                    disabled={this.state.ignoredEmployees.length === 0}>
                    Ignore Selected Employees
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  getFilteredEmployees() {

    const { positions, workdaysGroup } = this.state.employeesParameters;
    const employees = this.getEmployees(positions);
    const filterText = this.state.employeesTextFilter.toLowerCase();
    return employees.filter(employee => {
      const name = (employee.travellerName).toLowerCase();
      const employeeId = (employee.employeeId).toLowerCase();
      const workdaysGroupFilter = workdaysGroup == null || employee.workdaysGroup == workdaysGroup;
      const textFilter = name.indexOf(filterText) >= 0 || employeeId.startsWith(filterText);
      return workdaysGroupFilter && textFilter;
    });
  }

  renderEmployees() {

    const { positions, workdaysGroup } = this.state.employeesParameters;
    const filteredEmployees = this.getFilteredEmployees();

    let groupDescription = "?";
    if (workdaysGroup == null) {
      groupDescription = "all employees";
    } else {
      const preffix = GROUPS[workdaysGroup];
      let suffix;
      if (workdaysGroup == 0) {
        suffix = " or less days";
      } else if (workdaysGroup == GROUPS.length - 1) {
        suffix = " days plus";
      } else {
        suffix = `-${GROUPS[parseInt(workdaysGroup) + 1]} days`;
      }
      groupDescription = `employees with ${preffix}${suffix}`;
    }

    const periods = this.state.periods;
    const periodDescription = positions.length == 1 ?
      ` between ${dates.formatDate(periods[positions[0]].from)} and ${dates.formatDate(periods[positions[0]].to)}` :
      "";

    let positionsDescription = "?";
    if (positions) {
      const individualDescriptions = positions.map(position => {
        switch (position) {
        case POS_BRANCH: return "branch visitor";
        case POS_NON_TREATY: return "non-treaty country visitor";
        case POS_TREATY: return "treaty country visitor";
        case POS_UK: return "UK employee";
        case POS_UNKNOWN: return "unknown employee";
        case POS_EXPAT: return "UK expatriate";
        }
      });
      positionsDescription = individualDescriptions.join("/");
    }

    return (
      <div className="mintax-form">
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="form-group">
            <div className="row">
              <div className="col-xs-12">
                <p>{this.renderSign()}</p>
                <p>Showing {positionsDescription} days in the UK for {groupDescription}{periodDescription}.</p>
              </div>
            </div>
              <div className="row">
                <div className="col-xs-6 col-md-3">
                  <input className="form-control mintax-medium-field" placeholder="Filter"
                        value={this.state.employeesTextFilter} onChange={this.handleInputChange} name="employeesTextFilter" />
                </div>
              </div>
            </div>
            {filteredEmployees.length > 0 ? (
              <div className="form-group">
                <table className="table table-bordered table-striped">
                  <thead>
                    <tr>
                      <th style={{ width: "50pt", minWidth: "50pt" }}>Ignore</th>
                      <th style={{ width: "300pt", minWidth: "180pt" }}>Employee Name</th>
                      <th style={{ width: "120pt", minWidth: "120pt" }}>Employee ID</th>
                      <th style={{ width: "175pt", minWidth: "175pt" }}>Number of days in the UK</th>
                      <th className="mintax-actions-column"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEmployees.map(employee => (
                      <tr key={`${employee.travellerName}-${employee.employeeId}`}>
                        <td className="mintax-checkbox-column">
                          <input type="checkbox" checked={this.isEmployeeIgnored(employee)}
                                 onChange={e => this.toggleEmployeeIgnore(employee)} />
                        </td>
                        <td>{employee.travellerName}</td>
                        <td>{employee.employeeId}</td>
                        <td>{employee.days}</td>
                        <td className="mintax-actions-column">
                          <button type="button" className="btn btn-sm btn-default"><i className="glyphicon glyphicon-download" />{' '}Travel History</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>No records found</p>
            )}
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group">
            <span className="mintax-ajax-indicator" />
          </div>
          <div className="mintax-button-group">
            <button className="btn btn-warning"
                    onClick={() => this.ignoreEmployees()}
                    disabled={this.state.ignoredEmployees.length === 0}>
                    Ignore Selected Employees
            </button>
            <button className="btn btn-default"
                    onClick={() => this.setState({ viewingEmployees: false })}>Back</button>
          </div>
        </div>
      </div>
    );
  }

  render() {
    if (this.state.viewingEmployees) {
      return this.renderEmployees();
    } else {
      return this.renderReport();
    }
  }
}

export default ReportResults;
