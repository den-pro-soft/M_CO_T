import React, { Component } from 'react';
import ajax from '../shared/ajax';
import msgbox from '../shared/msgbox';
import dates from '../shared/dates';
import Scrollbars from './Scrollbars';


class Settings extends Component {
  constructor(props) {
    super(props);
    this.state = {
      changingPassword: false,
      passwordChange: {
        current: "",
        new: "",
        confirmation: "",
      }
    };
    this.changePassword = this.changePassword.bind(this);
    this.handlePasswordInputChange = this.handlePasswordInputChange.bind(this);
  }

  changePassword(event) {
    event.preventDefault();
    if (!this.state.changingPassword) {
      return;
    }
    const data = this.state.passwordChange;
    ajax.exec('login/password', 'PUT', data, event.target).then(() => {
      msgbox.alert("Your password has been successfully changed.").then(() => {
        this.setState({
          changingPassword: false,
          passwordChange: {
            current: "",
            new: "",
            confirmation: "",
          }
        });
      });
    });
  }

  handlePasswordInputChange(event) {
    const passwordChange = this.state.passwordChange;
    const target = event.target;
    const fieldName = target.name;
    const type = target.type;
    passwordChange[fieldName] = type === 'checkbox' ? target.checked : target.value;
    this.setState({ passwordChange });
  }

  renderPasswordChangeForm() {
    return [
      <div className="form-group" key="password-change-form-current">
          <label className="control-label col-sm-2">Current Password</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" type="password" value={this.state.passwordChange.current}
                   name="current" onChange={this.handlePasswordInputChange} />
          </div>
      </div>,
      <div className="form-group" key="password-change-form-new">
          <label className="control-label col-sm-2">New Password</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" type="password" value={this.state.passwordChange.new}
                   name="new" onChange={this.handlePasswordInputChange} />
            <p className="mintax-form-hint">
              <span className="glyphicon glyphicon-info-sign"/>{' '}
              Your new password should have a minimum length of 8 characters and 
              include at least 1 lowercase letter, 1 uppercase letter and 1 number
            </p>
          </div>
      </div>,
      <div className="form-group" key="password-change-form-confirmation">
          <label className="control-label col-sm-2">Confirm</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" type="password" value={this.state.passwordChange.confirmation}
                   name="confirmation" onChange={this.handlePasswordInputChange} />
          </div>
      </div>
    ];
  }

  renderNormalForm() {
    const info = this.props.accountInfo;
    return [
      <div className="form-group" key="settings-first-name">
          <label className="control-label col-sm-2">First Name</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" value={info.firstName} disabled={true} />
          </div>
      </div>,
      <div className="form-group" key="settings-second-name">
          <label className="control-label col-sm-2">Second Name</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" value={info.secondName} disabled={true} />
          </div>
      </div>,
      <div className="form-group" key="settings-company-name">
          <label className="control-label col-sm-2">Company Name</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" value={info.companyName} disabled={true} />
          </div>
      </div>,
      <div className="form-group" key="settings-company-address">
          <label className="control-label col-sm-2">Company Address</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <textarea className="form-control" rows={5} value={info.companyAddress} disabled={true} />
          </div>
      </div>,
      <div className="form-group" key="settings-contract-end-date">
          <label className="control-label col-sm-2">Contract end date</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" value={dates.formatDate(info.contractEndDate)} disabled={true} />
          </div>
      </div>,
      <div className="form-group" key="settings-work-email">
          <label className="control-label col-sm-2">Work Email</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <input className="form-control" value={info.workEmail} disabled={true} />
          </div>
      </div>,
      <div className="form-group" key="settings-password">
          <label className="control-label col-sm-2">Password</label>
          <div className="col-sm-6 col-md-5 col-lg-4">
            <button className="btn btn-default" onClick={() => this.setState({ changingPassword: true })}>Change</button>
          </div>
      </div>
    ];
  }

  render() {
    return (
      <form className="mintax-form form-horizontal" onSubmit={this.changePassword}>
        <Scrollbars>
          <div className="mintax-form-body">
            {this.state.changingPassword ?
              this.renderPasswordChangeForm() :
              this.renderNormalForm() }
          </div>
        </Scrollbars>
        {this.state.changingPassword ?
          <div className="mintax-form-footer">
            <div className="mintax-button-group-right">
              <button className="btn btn-default" type="button" onClick={() => this.setState({ changingPassword: false })}>Cancel</button>
              <button className="btn btn-primary" onClick={this.changePassword}>Save</button>
              <span className="mintax-ajax-indicator" />
            </div>
          </div> :
          <span />}
      </form>
    );
  }
}

export default Settings;
