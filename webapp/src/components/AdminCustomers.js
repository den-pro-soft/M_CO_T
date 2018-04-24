import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import ajax from '../shared/ajax';
import dates from '../shared/dates';
import msgbox from '../shared/msgbox';
import handleInputChange from '../shared/handleInputChange';
import AjaxError from './AjaxError';
import Scrollbars from './Scrollbars';


class AdminCustomers extends Component {
  constructor(props) {
    super(props);
    this.state = {
      customers: undefined,
      filter: "",
      showDisabled: false,
    };
    this.handleInputChange = handleInputChange.bind(this);
  }

  componentDidMount() {
    this.fetchCustomers();
  }

  fetchCustomers() {
    ajax.exec('admin/customers')
        .catch(() => this.setState({ customers: null }))
        .then(customers => this.setState({ customers }));
  }

  deleteCustomer(customer) {
    msgbox.confirm(`Do you really want to remove customer '${customer.name}'?`).then(() => {
      ajax.exec(`admin/customers/${customer.id}`, 'DELETE').then(() => {
        customer.active = false;
        const customers = this.state.customers;
        this.setState({ customers });
      })
    });
  }

  filteredCustomers() {
    const customers = this.state.customers;
    const filter = this.state.filter.toLowerCase();
    const showDisabled = this.state.showDisabled;
    return this.state.customers.filter(customer => {
      const name = (customer.name || "").toLowerCase();
      const textFilter = name.indexOf(filter) >= 0;
      const activeFilter = showDisabled || customer.active;
      return textFilter && activeFilter;
    });
  }

  render() {

    if (this.state.customers === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.customers === null) {
      return <AjaxError />
    }

    const filteredCustomers = this.filteredCustomers();

    return (
      <form className="mintax-form" onSubmit={this.send}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="form-group">
              <input className="form-control mintax-medium-field" placeholder="Filter"
                     value={this.state.filter} onChange={this.handleInputChange} name="filter" />
              <div className="checkbox">
                <label>
                  <input type="checkbox" checked={this.state.showDisabled}
                         onChange={this.handleInputChange} name="showDisabled" /> Show disabled customers
                </label>
              </div>
            </div>
            {filteredCustomers.length > 0 ? (
              <div className="form-group">
                <table className="table table-bordered table-striped">
                  <thead>
                    <tr>
                      <th style={{ width: "250pt", minWidth: "125pt" }}>Name</th>
                      <th style={{ width: "125pt", minWidth: "125pt" }}>Contract End Date</th>
                      <th className="mintax-actions-column"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCustomers.map(customer => (
                      <tr key={customer.id} className={customer.active ? "" : "mintax-inactive-row"}>
                          <td>{customer.name}</td>
                          <td>{dates.formatDate(customer.contractEndDate)}</td>
                          <td className="mintax-actions-column">
                              <Link to={`/admin/customers/${customer.id}`} className="btn btn-sm btn-default"><i className="glyphicon glyphicon-pencil" /></Link>{' '}
                              {customer.active ? (
                                <button type="button" className="btn btn-sm btn-default" onClick={() => this.deleteCustomer(customer)}><i className="glyphicon glyphicon-trash" /></button>
                              ) : <span />}
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
          <div className="mintax-button-group-right">
            <Link to="/admin/customers/new" className="btn btn-primary">New Customer</Link>
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
      </form>
    );
  }
}

export default AdminCustomers;
