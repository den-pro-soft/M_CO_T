import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import Select from 'react-select';
import ajax from '../shared/ajax';
import msgbox from '../shared/msgbox';
import dates from '../shared/dates';
import DatePickerInput from './DatePickerInput';
import Scrollbars from './Scrollbars';
import AjaxError from './AjaxError';


class AdminCustomerForm extends Component {
  constructor(props) {
    super(props);
    const customerId = props.match.params.customerId;
    this.state = {
      data: customerId ? undefined : {
        name: "",
        address: "",
        contractEndDate: "",
        active: true,
        applications: [],
      },
      applications: undefined,
    };
    this.handleDataInputChange = this.handleDataInputChange.bind(this);
    this.handleContractEndDateInputChange = this.handleContractEndDateInputChange.bind(this);
    this.handleApplicationsChange = this.handleApplicationsChange.bind(this);
    this.send = this.send.bind(this);
  }

  componentDidMount() {
    const customerId = this.props.match.params.customerId;
    if (customerId) {
      ajax.exec(`admin/customers/${customerId}`)
        .catch(() => this.setState({ data: null }))
        .then(data => this.setState({ data }));
    }
    ajax.exec('applications')
      .then(applications => {
        this.setState({
          applications: applications.map(app => ({
            label: app.name,
            value: app.id,
          }))
        });
      })
      .catch(() => this.setState({ applications: null }));
  }

  send(event) {
    event.preventDefault();
    const customerId = this.props.match.params.customerId;
    const data = this.state.data;
    const path = customerId ? `admin/customers/${customerId}` : 'admin/customers';
    const method = customerId ? 'PUT' : 'POST';
    ajax.exec(path, method, data, event.target).then(() => {
      msgbox.alert("The customer has been successfully saved.").then(() => {
        this.props.history.push("/admin/customers");
      });
    });
  }

  handleApplicationsChange(selection) {
    const data = this.state.data;
    data.applications = selection.map(sel => sel.value);
    this.setState({ data });
  }

  handleDataInputChange(event) {
    const data = this.state.data;
    const target = event.target;
    const fieldName = target.name;
    const type = target.type;
    data[fieldName] = type === 'checkbox' ? target.checked : target.value;
    this.setState({ data });
  }

  handleContractEndDateInputChange(eventOrValue) {
    const data = this.state.data;
    data.contractEndDate = eventOrValue && eventOrValue.target ? eventOrValue.target.value : eventOrValue;
    this.setState({ data });
  }

  render() {

    if (this.state.data === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data === null) {
      return <AjaxError />
    }

    return (
      <form className="mintax-form form-horizontal" onSubmit={this.send}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="form-group">
                <label className="control-label col-sm-2">Name</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <input className="form-control" value={this.state.data.name}
                           onChange={this.handleDataInputChange} name="name" />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2">Address</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <textarea className="form-control" rows={5} value={this.state.data.address}
                           onChange={this.handleDataInputChange} name="address" />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2">Contract end date</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <DatePickerInput className="form-control"
                           selected={dates.parse(this.state.data.contractEndDate)}
                           onChange={this.handleContractEndDateInputChange}
                           onChangeRaw={this.handleContractEndDateInputChange} />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2">Applications</label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <Select value={this.state.data.applications}
                            onChange={this.handleApplicationsChange}
                            multi={true}
                            isLoading={this.state.applications === undefined}
                            options={this.state.applications} />
                </div>
            </div>
            <div className="form-group">
                <label className="control-label col-sm-2"></label>
                <div className="col-sm-6 col-md-5 col-lg-4">
                    <div className="checkbox">
                      <label>
                          <input type="checkbox" checked={this.state.data.active}
                              onChange={this.handleDataInputChange} name="active" />
                          {' '}Active
                      </label>
                    </div>
                </div>
            </div>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group-right">
            <Link className="btn btn-default" type="button" to="/admin/customers">Cancel</Link>
            <button className="btn btn-primary">Save</button>
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
      </form>
    );
  }
}

export default AdminCustomerForm;
