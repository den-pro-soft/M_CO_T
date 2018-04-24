import React, { Component } from 'react';
import Select from 'react-select';
import _ from 'lodash'
import UnsavedDataHandler from './UnsavedDataHandler';
import PAYEInput from './PAYEInput';
import Scrollbars from './Scrollbars';
import AjaxError from './AjaxError';
import handleInputChange from '../shared/handleInputChange';
import ajax from '../shared/ajax';
import msgbox from '../shared/msgbox';
import numbers from '../shared/numbers';
import redirectTo from '../shared/redirectTo';


const newBranch = function () {
  return {
    name: "",
    country: null,
  };
};

const newCompany = function () {
  return {
      name: "",
      paye: "",
      trackingMethod: "",
      otherTrackingMethod: "",
      numberOfBranches: 0,
      branches: [],
      simplifiedPayroll: false,
      simplifiedPayrollPaye: "",
    };
};

class Company extends Component {
  constructor(props) {
    super(props);

    this.pristineData = null;
    this.state = {
      data: undefined,
      countries: undefined,
    };

    this.handleInputChange = handleInputChange.bind(this);
    this.handleNumberOfCompaniesChange = this.handleNumberOfCompaniesChange.bind(this);
    this.addCompany = this.addCompany.bind(this);
    this.fetchData = this.fetchData.bind(this);
    this.fetchCountries = this.fetchCountries.bind(this);
    this.send = this.send.bind(this);
  }

  componentDidMount() {
    this.fetchData();
    this.fetchCountries();
  }

  fetchData() {
    ajax.exec('company')
      .then(data => {
        if (!data) {
          data = {
            numberOfCompanies: 1,
            branchesOverseas: null,
            companies: [ newCompany() ],
            simplifiedAnnualPayroll: null,
            employeesOnAssignmentUK: null,
            anyNonTaxableEmployees: null,
          };
        }
        this.pristineData = _.cloneDeep(data);
        this.setState({ data });
      })
      .catch(() => {
        this.setState({ data: null });
      });
  }

  fetchCountries() {
    return ajax.exec('countries').then(countries => {
      this.setState({
        countries: countries.filter(country => country.code != 'GBR').map(country => {
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
    ajax.exec('company', 'PUT', data, event.target).then(() => {
      msgbox.alert("Your company data has been successfully saved.").then(() => {
        redirectTo('/uk-employees');
      });
    });
  }

  addCompany() {
    const data = this.state.data;
    this.applyNewNumberOfCompanies(data.companies.length + 1);
  }

  removeCompany(i) {
    const data = this.state.data;
    const companies = data.companies;
    companies.splice(i, 1);
    data.numberOfCompanies = companies.length;
    this.setState({ data });
  }

  removeBranch(i, j) {
    const data = this.state.data;
    const companies = data.companies;
    const company = companies[i];
    if (company.branches.length <= 1) {
      this.removeCompany(i);
    } else {
      const branches = company.branches;
      branches.splice(j, 1);
      company.numberOfBranches = branches.length;
      this.setState({ data });
    }
  }

  handleNumberOfCompaniesChange(event) {
    let numberOfCompanies = event.target.value;
    if (numberOfCompanies < 0) {
      numberOfCompanies = 0;
    }
    const data = this.state.data;
    data.numberOfCompanies = numberOfCompanies;
    this.setState({ data });
    this.applyNewNumberOfCompanies(Math.max(0, numberOfCompanies));
  }

  handleNumberOfBranchesChange(company, event) {
    company.numberOfBranches = event.target.value;
    if (company.numberOfBranches < 0) {
      company.numberOfBranches = 0;
    }
    const newNumberOfBranches = Math.max(0, company.numberOfBranches);
    const oldBranches = company.branches;
    const newBranches = [];
    for (let i = 0; i < newNumberOfBranches; i++) {
      if (i < oldBranches.length) {
        newBranches.push(oldBranches[i]);
      } else {
        newBranches.push(newBranch());
      }
    }
    company.branches = newBranches;
    this.setState({ data: this.state.data });
  }

  applyNewNumberOfCompanies(newNumberOfCompanies) {
    const data = this.state.data;
    const oldCompanies = data.companies;
    const newCompanies = [];
    for (let i = 0; i < newNumberOfCompanies; i++) {
      if (i < oldCompanies.length) {
        newCompanies.push(oldCompanies[i]);
      } else {
        newCompanies.push(newCompany());
      }
    }
    data.numberOfCompanies = newNumberOfCompanies;
    data.companies = newCompanies;
    this.setState({ data });
  }

  // this method is able to handle any change
  // in an object inside the data object
  handleDataInputChange(object, fieldName, event) {
    const target = event.target;
    const type = target.type;
    object[fieldName] = type === 'checkbox' ? target.checked : target.value;
    const data = this.state.data;
    this.setState({ data });
  }

  handleCountryChange(branch, selection) {
    branch.country = selection ? selection.value : null;
    const data = this.state.data;
    this.setState({ data });
  }

  renderCompaniesTable() {

    const hasMultipleCompanies = this.state.data.companies.length > 1;
    const hasBranches = this.state.data.branchesOverseas === 'Y';
    const rows = [];

    for (let i in this.state.data.companies) {
      const company = this.state.data.companies[i];

      const rowSpan = hasBranches ? company.branches.length : 0;
      const rowClasses = i % 2 == 0 ? "mintax-striped-row" : "";
      const companyCells = [
        <td key={"company-" + i + "-name"} rowSpan={rowSpan}>
          <input type="text" className="form-control" name="name"
                value={company.name} onChange={e => this.handleDataInputChange(company, "name", e)} />
        </td>,
        <td key={"company-" + i + "-paye"} rowSpan={rowSpan}>
          <PAYEInput className="form-control" name="paye"
                     value={company.paye} onChange={e => this.handleDataInputChange(company, "paye", e)} />
        </td>,
        <td key={"company-" + i + "-tracking-method"} rowSpan={rowSpan}>
          <select className="form-control" name="trackingMethod" value={company.trackingMethod} onChange={e => this.handleDataInputChange(company, "trackingMethod", e)}>
            <option></option>
            <option value="1">Corporate travel vendor</option>
            <option value="2">UK employee passes</option>
            <option value="3">UK register</option>
            <option value="4">Other</option>
          </select>
          {company.trackingMethod === '4' ?
            <input type="text" className="form-control mintax-margin-top"
                   name="otherTrackingMethod" value={company.otherTrackingMethod} onChange={e => this.handleDataInputChange(company, "otherTrackingMethod", e)}
                   placeholder="Please specify..." /> : []}
        </td>,
      ];

      if (!hasBranches) {
        rows.push(<tr key={"company-" + i} className={rowClasses}>
          {companyCells}
          <td className="mintax-actions-column">
            { hasMultipleCompanies ? (
              <button type="button" className="btn btn-sm btn-default" onClick={() => this.removeCompany(i)}><i className="glyphicon glyphicon-trash" /></button>
            ) : <span />}
          </td>
        </tr>);
      } else if (company.branches.length == 0) {
        rows.push(<tr key={"company-" + i} className={rowClasses}>
          {companyCells}
          <td>
            <select className="form-control" name="numberOfBranches" value={company.numberOfBranches} onChange={e => this.handleNumberOfBranchesChange(company, e)}>
              {numbers.range(21).map(n => <option key={n}>{n}</option>)}
            </select>
          </td>
          <td>
            <input type="text" className="form-control" disabled={true} />
          </td>
          <td>
            <Select disabled={true} />
          </td>
          <td className="mintax-actions-column">
            { hasMultipleCompanies ? (
              <button type="button" className="btn btn-sm btn-default" onClick={() => this.removeCompany(i)}><i className="glyphicon glyphicon-trash" /></button>
            ) : <span />}
          </td>
        </tr>);
      } else {
        for (let j = 0; j < company.branches.length; j++) {
          const branch = company.branches[j];
          const firstBranch = j == 0;
          rows.push(<tr key={"company-" + i + "-branch-" + j} className={rowClasses}>
            {firstBranch ? companyCells : []}
            {firstBranch ?
              <td key={"company-" + i + "-branches-oversea"} rowSpan={rowSpan}>
                <select className="form-control" name="numberOfBranches" value={company.numberOfBranches} onChange={e => this.handleNumberOfBranchesChange(company, e)}>
                  {numbers.range(21).map(n => <option key={n}>{n}</option>)}
                </select>
              </td> : []}
            <td>
              <input type="text" className="form-control" name="name"
                    disabled={company.numberOfBranches == 0}
                    value={branch.name} onChange={e => this.handleDataInputChange(branch, "name", e)} />
            </td>
            <td>
              <Select value={branch.country}
                      onChange={selection => this.handleCountryChange(branch, selection)}
                      disabled={company.numberOfBranches == 0}
                      isLoading={this.state.countries === undefined}
                      options={this.state.countries} />
            </td>
            <td className="mintax-actions-column">
              { hasMultipleCompanies || company.branches.length > 1 ? (          
                <button type="button" className="btn btn-sm btn-default" onClick={() => this.removeBranch(i, j)}><i className="glyphicon glyphicon-trash" /></button>
              ) : <span />}
            </td>
          </tr>);
        }
      }

    }

    return (
      <table className="table table-bordered">
        <thead>
          <tr>
            <th style={{ width: "250pt", minWidth: "125pt" }}>UK Employing Entity Name</th>
            <th style={{ width: "180pt", minWidth: "180pt" }}>PAYE Reference</th>
            <th style={{ width: "185pt", minWidth: "185pt" }}>Method of tracking business travellers to the UK</th>
            {hasBranches ? [
              <th style={{ width: "100pt", minWidth: "100pt" }} key="companies-number-of-branches-header">Number of overseas Branches</th>,
              <th style={{ width: "250pt", minWidth: "125pt" }} key="companies-branch-name-header">Name of Branch</th>,
              <th style={{ width: "300pt", minWidth: "200pt" }} key="companies-branch-country-header">Country Location of Branch</th>,
            ] : []}
            <th className="mintax-actions-column"></th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
        <tfoot>
          <tr>
            <td colSpan={hasBranches ? "6" : "3"}>
              <button type="button" className="btn btn-sm btn-default" onClick={this.addCompany}><span className="glyphicon glyphicon-plus" /></button>
            </td>
          </tr>
        </tfoot>
      </table>
    );
  }

  renderSimplifiedAnnualPayrollTable() {

    const rows = [];
    for (let i in this.state.data.companies) {
      const company = this.state.data.companies[i];
      rows.push(<tr key={i}>
        <td>
          <input type="text" className="form-control" value={company.name} disabled={true} />
        </td>
        <td className="mintax-checkbox-column">
          <input type="checkbox" checked={company.simplifiedPayroll} onChange={e => this.handleDataInputChange(company, "simplifiedPayroll", e)} />
        </td>
        <td>
          <PAYEInput className="form-control" name="paye" disabled={!company.simplifiedPayroll}
                     value={company.simplifiedPayrollPaye} onChange={e => this.handleDataInputChange(company, "simplifiedPayrollPaye", e)} />
        </td>
        <td className="mintax-actions-column">
        </td>
      </tr>);
    }

    return rows;
  }

  render() {

    if (this.state.data === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data === null) {
      return <AjaxError />
    }

    let rowNumber = 1;
    return (
      <form className="mintax-form" onSubmit={this.send}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="form-group">
              <label htmlFor="numberOfCompanies">{rowNumber++}. How many employing entities/PAYE references does the Group have in the UK?</label>
              <select id="numberOfCompanies" className="form-control mintax-small-field" value={this.state.data.numberOfCompanies} onChange={this.handleNumberOfCompaniesChange}>
                {numbers.range(51).slice(1).map(n => <option key={n}>{n}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>{rowNumber++}. Do any of the UK Tax Resident companies have overseas (non-UK) branches?</label>
              <div className="radio">
                <label><input type="radio" name="branchesOverseas" checked={this.state.data.branchesOverseas === 'Y'} onChange={e => this.handleDataInputChange(this.state.data, 'branchesOverseas', e)} value="Y" /> Yes</label>{' '}
                <label><input type="radio" name="branchesOverseas" checked={this.state.data.branchesOverseas === 'N'} onChange={e => this.handleDataInputChange(this.state.data, 'branchesOverseas', e)} value="N" /> No</label>
              </div>
            </div>
            <div className="form-group">
              <label>{rowNumber++}. Please complete the table below with the relevant employing entity information and PAYE references.</label>
              {this.renderCompaniesTable()}
            </div>
            <div className="form-group">
              <label>{rowNumber++}. Does the Company have a simplified annual payroll for business travellers from non-treaty/overseas branches?</label>
              <div className="radio">
                <label><input type="radio" name="simplifiedAnnualPayroll" checked={this.state.data.simplifiedAnnualPayroll === 'Y'} onChange={e => this.handleDataInputChange(this.state.data, 'simplifiedAnnualPayroll', e)} value="Y" /> Yes</label>{' '}
                <label><input type="radio" name="simplifiedAnnualPayroll" checked={this.state.data.simplifiedAnnualPayroll === 'N'} onChange={e => this.handleDataInputChange(this.state.data, 'simplifiedAnnualPayroll', e)} value="N" /> No</label>
              </div>
            </div>
            {this.state.data.simplifiedAnnualPayroll === 'Y' ? <div className="form-group">
              <label>{rowNumber++}. Please confirm the entity name(s) that operate the simplified payroll(s):</label>
              <table className="table table-bordered table-striped">
                <thead>
                  <tr>
                    <th style={{ width: "250pt", minWidth: "125pt" }}>UK Employing Entity Name</th>
                    <th style={{ width: "125pt", minWidth: "125pt" }}>Simplified Payroll Scheme set up?</th>
                    <th style={{ width: "180pt", minWidth: "180pt" }}>PAYE Reference</th>
                    <th className="mintax-actions-column"></th>
                  </tr>
                </thead>
                <tbody>
                  {this.renderSimplifiedAnnualPayrollTable()}
                </tbody>
              </table>
            </div> : <div />}
            <div className="form-group">
              <label>{rowNumber++}. Does the Company have any employees on assignment in the UK?</label>
              <div className="radio">
                <label><input type="radio" name="employeesOnAssignmentUK" checked={this.state.data.employeesOnAssignmentUK === 'Y'} onChange={e => this.handleDataInputChange(this.state.data, 'employeesOnAssignmentUK', e)} value="Y" /> Yes</label>{' '}
                <label><input type="radio" name="employeesOnAssignmentUK" checked={this.state.data.employeesOnAssignmentUK === 'N'} onChange={e => this.handleDataInputChange(this.state.data, 'employeesOnAssignmentUK', e)} value="N" /> No</label>
              </div>
            </div>
            <div className="form-group">
              <label>{rowNumber++}. Does the Company have any employees on the UK payroll who are not taxable in the UK e.g. because they are on a No Tax (NT) code or are on short term assignment in the UK?</label>
              <div className="radio">
                <label><input type="radio" name="anyNonTaxableEmployees" checked={this.state.data.anyNonTaxableEmployees === 'Y'} onChange={e => this.handleDataInputChange(this.state.data, 'anyNonTaxableEmployees', e)} value="Y" /> Yes</label>{' '}
                <label><input type="radio" name="anyNonTaxableEmployees" checked={this.state.data.anyNonTaxableEmployees === 'N'} onChange={e => this.handleDataInputChange(this.state.data, 'anyNonTaxableEmployees', e)} value="N" /> No</label>
              </div>
            </div>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group-right">
            <button className="btn btn-primary">Save</button>
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
        <UnsavedDataHandler verifier={() => !_.isEqual(this.pristineData, this.state.data)} />
      </form>
    );
  }
}

export default Company;
