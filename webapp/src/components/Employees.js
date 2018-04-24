import React, { Component } from 'react';
import UnsavedDataHandler from './UnsavedDataHandler';
import DatePickerInput from './DatePickerInput';
import ajax from '../shared/ajax';
import dates from '../shared/dates';
import msgbox from '../shared/msgbox';
import numbers from '../shared/numbers';
import handleInputChange from '../shared/handleInputChange';
import redirectTo from '../shared/redirectTo';
import AjaxError from './AjaxError';
import Scrollbars from './Scrollbars';
import FileUpload from './FileUpload';
import PagingControls from './PagingControls';


const newArrangement = function () {
  return {
    category: "",
    effectiveFrom: null,
    effectiveTo: null,
  };
};

const newFilter = function (category, showDuplicatesOnly, showDuplicateIDsOnly) {
  return {
    filterText: "",
    filterCategory: category || "",
    currentPage: 0,
    showDuplicatesOnly: showDuplicatesOnly || false,
    showDuplicateIDsOnly: showDuplicateIDsOnly || false,
  };
};


class Employees extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: undefined,
      filterText: "",
      filterCategory: "",
      showDuplicatesOnly: false,
      showDuplicateIDsOnly: false,
      currentPage: 0,
      managingEmployees: false,
      hasChangedEmployees: false,
      employeesRemoved: [],
    };
    this.fetchData = this.fetchData.bind(this);
    this.downloadSpreadsheet = this.downloadSpreadsheet.bind(this);
    this.deleteSpreadsheet = this.deleteSpreadsheet.bind(this);
    this.save = this.save.bind(this);
    this.manageEmployees = this.manageEmployees.bind(this);
    this.handleInputChange = handleInputChange.bind(this);
    this.renderEmployeeRow = this.renderEmployeeRow.bind(this);
    this.renderEmployeeManagement = this.renderEmployeeManagement.bind(this);
    this.handleArrangementDateInputChange = this.handleArrangementDateInputChange.bind(this);
    this.handleDataInputChange = this.handleDataInputChange.bind(this);
    this.addEmployee = this.addEmployee.bind(this);
  }

  componentDidMount() {
    this.fetchData(false);
  }

  hasPendingChanges() {
    return (this.state.data && !this.state.data.active) || this.state.hasChangedEmployees;
  }

  collectEmployeeOperations() {
    const employees = this.state.data.employees || [];
    const additions = [];
    const changes = [];
    employees.forEach(employee => {
      if (employee.new) {
        additions.push(employee);
      } else if (employee.changed) {
        changes.push(employee);
      }
    });
    const removals = this.state.employeesRemoved;
    return {
      additions, changes, removals
    };
  }

  save() {
    if (this.state.data.id) {
      const employeeOperations = this.collectEmployeeOperations();
      ajax.exec(`employees/${this.state.data.id}/activate`, "POST", employeeOperations, this.form)
        .then(({ foundAnyDuplication }) => {
          let msg = "Your employee data has been successfully saved.";
          if (foundAnyDuplication) {
            msg += " At least two records had the same name/ID and were combined. Please go back to the employee list and update their working arrangements if needed.";
          }
          msgbox.alert(msg);
        })
        .then(() => redirectTo('/traveller-data/data-upload'));
    } else {
      ajax.exec('employees/deactivate-current', "POST", undefined, this.form)
        .then(() => msgbox.alert("Your employee data has been successfully saved."))
        .then(() => this.fetchData(false));
    }
  }

  manageEmployees(category, showDuplicatesOnly, showDuplicateIDsOnly) {
    const state = newFilter(category, showDuplicatesOnly, showDuplicateIDsOnly);
    state.managingEmployees = true;
    this.setState(state);
  }

  deleteArrangement(employee, arrangement) {

    // if there is only one arrangement remaining
    // we are removing the employee itself!
    const removingArrangement = employee.arrangements.length > 1;
    const data = this.state.data;
    if (removingArrangement) {
      const idx = employee.arrangements.indexOf(arrangement);
      msgbox.confirm(`Do you really want to remove work arrangement #${idx + 1} ` +
                     `from employee ${employee.name || 'Unnamed'} (${employee.employeeId || 'no ID'})?`).then(() => {
        employee.arrangements.splice(idx, 1);
        if (employee.arrangements.length == 1) {
          employee.arrangements[0].effectiveFrom = null;
          employee.arrangements[0].effectiveTo = null;
        }
        if (!employee.new) {
          employee.changed = true;
        }
        this.setState({ data, hasChangedEmployees: true });
      });
    } else {
      msgbox.confirm(`Do you really want to remove employee ${employee.name || 'Unnamed'}` +
                     ` (${employee.employeeId || 'no ID'})?`).then(() => {
        const idx = data.employees.indexOf(employee);
        data.employees.splice(idx, 1);
        if (!employee.new) {
          this.state.employeesRemoved.push(employee.id);
        }
        this.setState({ data, hasChangedEmployees: true });
      });
    }
  }

  toggleChangeInWorkingArrangements(employee) {
    const data = this.state.data;
    if (employee.arrangements.length == 1) {
      if (!employee.new) {
        employee.changed = true;
      }
      employee.arrangements.push(newArrangement());
      this.setState({ data, hasChangedEmployees: true });
    } else {
      msgbox.confirm('This will remove all but the first work arrangement for ' +
                     `employee ${employee.name || 'Unnamed'} (${employee.employeeId || 'no ID'}). ` +
                     'Are you sure you want to proceed?').then(() => {
        if (!employee.new) {
          employee.changed = true;
        }
        employee.arrangements.splice(1);
        employee.arrangements[0].effectiveFrom = null;
        employee.arrangements[0].effectiveTo = null;
        this.setState({ data, hasChangedEmployees: true });
      });
    }
  }

  fetchData(unsaved) {
    const state = newFilter();
    state.data = undefined;
    state.employeesRemoved = [];
    state.hasChangedEmployees = false;
    state.managingEmployees = false;
    this.setState(state);
    ajax.exec('employees', 'GET', { unsaved })
      .then(data => {
        this.setState({ data });
        ajax.exec('employees/details', 'GET', { unsaved })
          .then(employees => {
            const data = this.state.data;
            data.employees = employees;
            this.setState({ data });
          })
          .catch(() => {
            const data = this.state.data;
            data.employees = null;
            this.setState({ data });
          });
      })
      .catch(() => this.setState({ data: null }));
  }

  downloadSpreadsheet() {
    const data = this.state.data;
    const fileName = data.fileName;
    const id = data.id;
    ajax.download(`employees/${id}/download`, fileName);
  }

  handleDataInputChange(subject, event, relatedEmployee) {
    const target = event.target;
    const fieldName = target.name;
    const type = target.type;
    subject[fieldName] = type === 'checkbox' ? target.checked : target.value;
    const data = this.state.data;
    if (!relatedEmployee.new) {
      relatedEmployee.changed = true;
    }
    this.setState({ data, hasChangedEmployees: true });
  }

  handleArrangementDateInputChange(eventOrValue, arrangement, fieldName, relatedEmployee) {
    arrangement[fieldName] = eventOrValue && eventOrValue.target ? eventOrValue.target.value : eventOrValue;
    const data = this.state.data;
    if (!relatedEmployee.new) {
      relatedEmployee.changed = true;
    }
    this.setState({ data, hasChangedEmployees: true });
  }

  deleteSpreadsheet() {
    msgbox.confirm('Please confirm that you would like to delete all employee data which has been uploaded?').then(() => {
      const data = this.state.data;
      data.id = null;
      data.dateOfLastUpload = null;
      data.fileName = null;
      data.ukEmployees = null;
      data.overseasBranchEmployees = null;
      data.ukExpatriates = null;
      data.ntStaEmployees = null;
      data.active = false;
      data.employees = [];
      this.setState({ data, hasChangedEmployees: false, employeesRemoved: [] });
    });
  }

  getFilteredEmployees() {
    const employees = this.state.data.employees;
    const filterText = this.state.filterText.toLowerCase();
    const filterCategory = this.state.filterCategory;
    const showDuplicatesOnly = this.state.showDuplicatesOnly;
    const showDuplicateIDsOnly = this.state.showDuplicateIDsOnly;
    return employees.filter(employee => {
      const name = (employee.name).toLowerCase();
      const employeeId = (employee.employeeId).toLowerCase();
      const textFilter = name.indexOf(filterText) >= 0 ||
        employeeId.startsWith(filterText);
      let categoryFilter = filterCategory == '';
      if (!categoryFilter) {
        for (const idx in employee.arrangements) {
          if (employee.arrangements[idx].category == filterCategory) {
            categoryFilter = true;
            break;
          }
        }
      }
      const duplicatesOnlyFilter = !showDuplicatesOnly || employee.duplicated;
      const duplicateIDsOnlyFilter = !showDuplicateIDsOnly || employee.duplicatedId;
      return textFilter && categoryFilter && duplicatesOnlyFilter && duplicateIDsOnlyFilter;
    });
  }

  addEmployee() {
    const data = this.state.data;
    data.employees.splice(0, 0, {
      id: numbers.guid(),
      name: "",
      employeeId: "",
      arrangements: [ newArrangement() ],
      new: true,
    });
    const state = newFilter();
    state.data = data;
    state.hasChangedEmployees = true;
    this.formBody.scrollIntoView();
    this.setState(state);
  }

  addArrangement(employee, after) {
    const idx = employee.arrangements.indexOf(after);
    employee.arrangements.splice(idx + 1, 0, newArrangement());
    const data = this.state.data;
    if (!employee.new) {
      employee.changed = true;
    }
    this.setState({ data, hasChangedEmployees: true });
  }

  renderDateOfLastUpload() {
    if (!this.state.data.dateOfLastUpload) {
      return <span>N/A</span>
    }
    return (
      <span>{dates.formatDateTime(this.state.data.dateOfLastUpload)}</span>
    );
  }

  renderSpreadsheetName() {
    if (!this.state.data.fileName) {
      return <span>N/A</span>
    }
    return (
      <div>
        <p>
          <a className="mintax-pointer" onClick={this.downloadSpreadsheet}>{this.state.data.fileName}</a>
        </p>
      </div>
    );
  }

  downloadDataTemplate() {
    ajax.download('employees/data-template', 'Employees.xlsx');
  }

  renderEmployeeCount(count, enabled, label, categoryId) {
    if (!enabled && !count) {
      return <span>N/A - No {label}</span>;
    } else if (!count) {
      return <span className="mintax-danger">Incomplete</span>;
    } else {
      return <a className="mintax-pointer" onClick={e => this.manageEmployees(categoryId)}>
        <span className="mintax-success">
          {count} {count > 1 ? "employees" : "employee"}
        </span>
      </a>;
    }
  }

  renderDuplicateCount() {
    if (!this.state.data.id) {
      return <td><span className="mintax-success">0 employees</span></td>;
    }
    if (this.state.data.employees == undefined) {
      return <td className="mintax-ajax-in-progress" />;
    } else if (this.state.data.employees == null) {
      return <td><AjaxError /></td>;
    } else {
      let duplicates = 0;
      this.state.data.employees.forEach(employee => {
        if (employee.duplicated) {
          duplicates++;
        }
      });
      if (duplicates == 0) {
        return <td><span className="mintax-success">0 employees</span></td>;
      } else {
        return (
          <td>
            <a className="mintax-pointer" onClick={e => this.manageEmployees(undefined, true, false)}>
              <span className="mintax-danger">
                {duplicates} {duplicates > 1 ? "employees" : "employee"}
              </span>
            </a>
          </td>
        );
      }
    } 
  }

  renderDuplicateIDCount() {
    if (!this.state.data.id) {
      return <td><span className="mintax-success">0 employees</span></td>;
    }
    if (this.state.data.employees == undefined) {
      return <td className="mintax-ajax-in-progress" />;
    } else if (this.state.data.employees == null) {
      return <td><AjaxError /></td>;
    } else {
      let duplicates = 0;
      this.state.data.employees.forEach(employee => {
        if (employee.duplicatedId) {
          duplicates++;
        }
      });
      if (duplicates == 0) {
        return <td><span className="mintax-success">0 employees</span></td>;
      } else {
        return (
          <td>
            <a className="mintax-pointer" onClick={e => this.manageEmployees(undefined, false, true)}>
              <span className="mintax-danger">
                {duplicates} {duplicates > 1 ? "employees" : "employee"}
              </span>
            </a>
          </td>
        );
      }
    } 
  }

  renderEmployeeUpload() {
    return (
      <div className="mintax-form" ref={el => this.form = el}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="row">
              <div className="col-xs-12">
                <p>Please complete and upload the <a className="mintax-pointer" onClick={this.downloadDataTemplate}>employee data template</a>.
                This will help to improve the accuracy of the reporting and minimise the number of “additional
                clarifications” and “unknowns” arising when the traveller data is uploaded and analysed.</p>
              </div>
            </div>
            <table className="table table-bordered">
              <thead>
                <tr>
                  <th style={{ width: "250pt", minWidth: "150pt" }}>Upload Data</th>
                  <th style={{ width: "150pt", minWidth: "150pt" }}>Spreadsheet Name</th>
                  <th style={{ width: "150pt", minWidth: "150pt" }}>Date Uploaded</th>
                  <th style={{ width: "185pt", minWidth: "185pt" }}>Employee Categories</th>
                  <th style={{ width: "250pt", minWidth: "185pt" }}>Number of employees</th>
                  <th className="mintax-actions-column"></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td rowSpan={6}><FileUpload to="employees" onBatchCompleted={() => this.fetchData(true)} /></td>
                  <td rowSpan={6}>
                    {this.renderSpreadsheetName()}
                  </td>
                  <td rowSpan={6}>{this.renderDateOfLastUpload()}</td>
                  <td>UK Employees</td>
                  <td>
                    {this.renderEmployeeCount(this.state.data.ukEmployees, true, "UK Employees", 1)}
                  </td>
                </tr>
                <tr>
                  <td>Overseas Branch Employees</td>
                  <td>
                    {this.renderEmployeeCount(this.state.data.overseasBranchEmployees, this.state.data.overseasBranchEmployeesEnabled, "Overseas Branch Employees", 2)}
                  </td>
                </tr>
                <tr>
                  <td>UK Expatriates</td>
                  <td>
                    {this.renderEmployeeCount(this.state.data.ukExpatriates, this.state.data.ukExpatriatesEnabled, "UK Expatriates", 3)}
                  </td>
                </tr>
                <tr>
                  <td>NT and/or STA Employees</td>
                  <td>
                    {this.renderEmployeeCount(this.state.data.ntStaEmployees, this.state.data.ntStaEmployeesEnabled, "NT and/or STA Employees", 4)}
                  </td>
                </tr>
                <tr>
                  <td>
                    Duplicates
                    {' '}
                    <span className="mintax-hint glyphicon glyphicon-info-sign"
                          title="These employees are currently appearing on multiple worksheets which may cause errors in tracking their UK days. Please click on the “Manage Employees” button and update this data accordingly." />
                  </td>
                  {this.renderDuplicateCount()}
                </tr>
                <tr>
                  <td>
                    Duplicate employee IDs
                    {' '}
                    <span className="mintax-hint glyphicon glyphicon-info-sign"
                          title="These employees does not currently have a unique ID. Please click on the “Manage Employees” button and update this data accordingly." />
                  </td>
                  {this.renderDuplicateIDCount()}
                </tr>
              </tbody>
            </table>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group">
            {this.state.data && this.state.data.fileName ? (
              <button type="button" className="btn btn-default" onClick={() => this.manageEmployees()}>
                <i className="glyphicon glyphicon-search" />
                {' '}
                Manage Employees
              </button>
            ) : <span />}
            <button className="btn btn-primary"
                    onClick={this.save}
                    disabled={!this.hasPendingChanges()}
                    title={!this.hasPendingChanges() ? "There is no unsaved changes" : ""}>Save</button>
            <span className="mintax-ajax-indicator" />
          </div>
          <div className="mintax-button-group">
            {this.state.data && this.state.data.fileName ? (
              <button type="button" className="btn btn-danger" onClick={this.deleteSpreadsheet}>
                <i className="glyphicon glyphicon-trash" />
                {' '}
                Delete Data
              </button>
            ) : <span />}
          </div>
        </div>
        <UnsavedDataHandler verifier={() => this.hasPendingChanges()} />
      </div>
    );
  }

  renderArrangementCells(arrangement, employee) {
    return [
      <td key="category">
        <div className="input-group">
          <select className="form-control" name="category" value={arrangement.category}
                  onChange={e => this.handleDataInputChange(arrangement, e, employee)}>
            <option></option>
            <option value="1">UK Employee</option>
            <option value="2">Overseas Branch Employee</option>
            <option value="3">UK Expatriate</option>
            <option value="4">NT and/or STA Employee</option>
          </select>
          {employee.arrangements.length > 1 ? (
            <div className="input-group-btn">
              <button className="btn btn-default" onClick={() => this.addArrangement(employee, arrangement)}>
                <span className="glyphicon glyphicon-plus" />
              </button>
            </div>
          ) : <span />}
        </div>
      </td>,
      <td key="effective-from" className="mintax-datepicker-cell-fixer">
        <DatePickerInput className="form-control" disabled={employee.arrangements.length == 1}
                  selected={dates.parse(arrangement.effectiveFrom)}
                  onChange={value => this.handleArrangementDateInputChange(value, arrangement, 'effectiveFrom', employee)}
                  onChangeRaw={event => this.handleArrangementDateInputChange(event, arrangement, 'effectiveFrom', employee)} />
      </td>,
      <td key="effective-to" className="mintax-datepicker-cell-fixer">
        <DatePickerInput className="form-control" disabled={employee.arrangements.length == 1}
                  selected={dates.parse(arrangement.effectiveTo)}
                  onChange={value => this.handleArrangementDateInputChange(value, arrangement, 'effectiveTo', employee)}
                  onChangeRaw={event => this.handleArrangementDateInputChange(event, arrangement, 'effectiveTo', employee)} />
      </td>
    ];
  }

  renderEmployeeRow(employee, i) {
    let rowClasses = i % 2 == 0 ? "mintax-striped-row" : "";
    if (employee.duplicated || employee.duplicatedId) {
      rowClasses += " mintax-invalid-row";
    }
    const firstArrangement = employee.arrangements[0];
    const rows = [
      <tr key={employee.id} className={rowClasses}>
          <td rowSpan={employee.arrangements.length}>
            <input type="text" className="form-control" name="name"
                    value={employee.name} onChange={e => this.handleDataInputChange(employee, e, employee)} />
          </td>
          <td rowSpan={employee.arrangements.length}>
            <input type="text" className="form-control" name="employeeId"
                    value={employee.employeeId} onChange={e => this.handleDataInputChange(employee, e, employee)} />
          </td>
          <td className="mintax-checkbox-column" rowSpan={employee.arrangements.length}>
            <input type="checkbox" checked={employee.arrangements.length > 1}
                    onChange={e => this.toggleChangeInWorkingArrangements(employee)} />
          </td>
          {this.renderArrangementCells(firstArrangement, employee)}
          <td className="mintax-actions-column">
              <button type="button" className="btn btn-sm btn-default"
                      onClick={() => this.deleteArrangement(employee, firstArrangement)}><i className="glyphicon glyphicon-trash" /></button>
          </td>
      </tr>
    ];
    for (let idx = 1; idx < employee.arrangements.length; idx++) {
      const arrangement = employee.arrangements[idx];
      rows.push((
        <tr key={`${employee.id}-arrangement-${idx}`} className={rowClasses}>
          {this.renderArrangementCells(arrangement, employee)}
          <td className="mintax-actions-column">
            <button type="button" className="btn btn-sm btn-default"
                    onClick={() => this.deleteArrangement(employee, arrangement)}><i className="glyphicon glyphicon-trash" /></button>
          </td>
        </tr>
      ));
    }
    return rows;
  }

  renderEmployeeManagement() {

    if (this.state.data.employees === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data.employees === null) {
      return <AjaxError />
    }

    const filteredEmployees = this.getFilteredEmployees();
    const pagedEmployees = PagingControls.getPagedResults(filteredEmployees, this.state.currentPage);
    return (
      <div className="mintax-form" ref={el => this.form = el}>
        <Scrollbars>
          <div className="mintax-form-body" ref={e => this.formBody = e}>
            <div className="row">
              <div className="col-xs-12">
                <p>This section should be used to resolve the “Duplicate” employees who have multiple working arrangements or share the same ID.
                  {' '}You can also add or delete employees as required.</p>
              </div>
            </div>
            <div className="form-group">
              <div className="row">
                <div className="col-xs-6 col-md-3">
                  <input className="form-control mintax-medium-field" placeholder="Filter"
                        value={this.state.filterText} onChange={this.handleInputChange} name="filterText" />
                </div>
                <div className="col-xs-6 col-md-4 col-lg-3">
                  <select className="form-control" name="filterCategory"
                        value={this.state.filterCategory}
                        onChange={this.handleInputChange}>
                    <option value="">All Arrangement Categories</option>
                    <option value="1">UK Employees</option>
                    <option value="2">Overseas Branch Employees</option>
                    <option value="3">UK Expatriates</option>
                    <option value="4">NT and/or STA Employees</option>
                  </select>
                </div>
              </div>
              <div className="row">
                <div className="col-xs-6 col-md-3">
                  <div className="checkbox">
                    <label>
                      <input type="checkbox" checked={this.state.showDuplicatesOnly}
                              onChange={this.handleInputChange} name="showDuplicatesOnly" /> Show duplicates only
                    </label>
                  </div>
                </div>
                <div className="col-xs-6 col-md-3">
                  <div className="checkbox">
                    <label>
                      <input type="checkbox" checked={this.state.showDuplicateIDsOnly}
                              onChange={this.handleInputChange} name="showDuplicateIDsOnly" /> Show duplicate IDs only
                    </label>
                  </div>
                </div>
              </div>
            </div>
            {filteredEmployees.length > 0 ? (
              <div className="form-group">
                <table className="table table-bordered">
                  <thead>
                    <tr className="mintax-transparent-row">
                      <td colSpan={6}>
                        <div className="mintax-left-right">
                          <button type="button" className="btn btn-sm btn-default" onClick={this.addEmployee}>Add Employee</button>
                          <PagingControls currentPage={this.state.currentPage}
                                          total={filteredEmployees.length}
                                          onPageClick={newPage => this.setState({ currentPage: newPage })} />
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <th style={{ width: "180pt", minWidth: "180pt" }}>Employee Name</th>
                      <th style={{ width: "120pt", minWidth: "120pt" }}>Employee ID</th>
                      <th style={{ width: "100pt", minWidth: "100pt" }}>Multiple Working Arrangements</th>
                      <th style={{ width: "230pt", minWidth: "230pt" }}>Working Arrangement Category</th>
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
                    {pagedEmployees.map(this.renderEmployeeRow)}
                  </tbody>
                  <tfoot>
                    <tr className="mintax-transparent-row">
                      <td colSpan={6}>
                        <PagingControls currentPage={this.state.currentPage}
                                        total={filteredEmployees.length}
                                        onPageClick={newPage => this.setState({ currentPage: newPage })} />
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            ) : (
              <p>No records found</p>
            )}
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group">
            <button className="btn btn-primary"
                    onClick={this.save}
                    disabled={!this.hasPendingChanges()}
                    title={!this.hasPendingChanges() ? "There is no unsaved changes" : ""}>Save</button>
            <span className="mintax-ajax-indicator" />
          </div>
          <div className="mintax-button-group">
            <button className="btn btn-default"
                    onClick={() => this.setState({ managingEmployees: false })}>Back</button>
          </div>
        </div>
        <UnsavedDataHandler verifier={() => this.hasPendingChanges()} />
      </div>
    );
  }

  render() {

    if (this.state.data === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data === null) {
      return <AjaxError />
    }

    if (this.state.managingEmployees) {
      return this.renderEmployeeManagement();
    } else {
      return this.renderEmployeeUpload();
    }
  }
}

export default Employees;
