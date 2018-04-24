import React, { Component } from 'react';
import Select from 'react-select';
import { Link } from 'react-router-dom';
import ajax from '../shared/ajax';
import msgbox from '../shared/msgbox';
import dates from '../shared/dates';
import DatePickerInput from './DatePickerInput';
import Scrollbars from './Scrollbars';
import AjaxError from './AjaxError';


class AdminUserForm extends Component {
  constructor(props) {
    super(props);
    const userId = props.match.params.userId;
    this.state = {
      data: userId ? undefined : {
        firstName: "",
        secondName: "",
        customerId: null,
        workEmail: "",
        password: "",
        active: true,
        admin: false,
      },
      customers: undefined,
    };
    this.handleDataInputChange = this.handleDataInputChange.bind(this);
    this.generatePassword = this.generatePassword.bind(this);
    this.send = this.send.bind(this);
    this.handleCustomerChange = this.handleCustomerChange.bind(this);
  }

  componentDidMount() {
    const userId = this.props.match.params.userId;
    if (userId) {
      ajax.exec(`admin/users/${userId}`)
        .then(data => {
            data.password = ""; // special case
            this.setState({ data });
        })
        .catch(() => this.setState({ data: null }));
    }
    ajax.exec('admin/customers')
      .catch(() => this.setState({ customers: null }))
      .then(customers => this.setState({
        customers: customers.map(customer => {
          return {
            value: customer.id,
            label: customer.name,
          };
        })
      }));
  }

  send(event) {
    event.preventDefault();
    const userId = this.props.match.params.userId;
    const data = this.state.data;
    const path = userId ? `admin/users/${userId}` : 'admin/users';
    const method = userId ? 'PUT' : 'POST';
    ajax.exec(path, method, data, event.target).then(() => {
      msgbox.alert("The user has been successfully saved.").then(() => {
        this.props.history.push("/admin/users");
      });
    });
  }

  handleDataInputChange(event) {
    const data = this.state.data;
    const target = event.target;
    const fieldName = target.name;
    const type = target.type;
    data[fieldName] = type === 'checkbox' ? target.checked : target.value;
    this.setState({ data });
  }

  handleCustomerChange(selection) {
    const data = this.state.data;
    data.customerId = selection ? selection.value : null;
    this.setState({ data });
  }

  generatePassword() {
    // https://stackoverflow.com/questions/1349404/generate-random-string-characters-in-javascript
    let text = "";
    const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < 16; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    const data = this.state.data;
    data.password = text;
    this.setState({ data });
  }

  render() {

    if (this.state.data === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data === null) {
      return <AjaxError />
    }

    const userId = this.props.match.params.userId;
    return (
      <form className="mintax-form form-horizontal" onSubmit={this.send}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="form-group">
                <label className="control-label col-sm-2">Customer</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                      <Select value={this.state.data.customerId}
                              onChange={this.handleCustomerChange}
                              disabled={userId !== undefined}
                              isLoading={this.state.customers === undefined}
                              options={this.state.customers} />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2">First Name</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <input className="form-control" value={this.state.data.firstName}
                           onChange={this.handleDataInputChange} name="firstName" />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2">Second Name</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <input className="form-control" value={this.state.data.secondName}
                           onChange={this.handleDataInputChange} name="secondName" />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2">Work Email</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <input className="form-control" value={this.state.data.workEmail}
                           onChange={this.handleDataInputChange} name="workEmail" />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2">Password</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <div className="input-group">
                        <input className="form-control" value={this.state.data.password}
                            onChange={this.handleDataInputChange} name="password"
                            placeholder={this.props.match.params.userId ? "Leave blank to keep unchanged" : ""} />
                        <span className="input-group-btn">
                            <button className="btn btn-default" type="button" onClick={this.generatePassword}>Generate</button>
                        </span>
                    </div>
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2"></label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <div className="checkbox-inline">
                      <label>
                          <input type="checkbox" checked={this.state.data.active}
                              onChange={this.handleDataInputChange} name="active" />
                          {' '}Active
                      </label>
                    </div>
                    <div className="checkbox-inline">
                      <label>
                          <input type="checkbox" checked={this.state.data.admin}
                              onChange={this.handleDataInputChange} name="admin" />
                          {' '}Admin
                      </label>
                    </div>
                </div>
            </div>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group-right">
            <Link className="btn btn-default" type="button" to="/admin/users">Cancel</Link>
            <button className="btn btn-primary">Save</button>
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
      </form>
    );
  }
}

export default AdminUserForm;
