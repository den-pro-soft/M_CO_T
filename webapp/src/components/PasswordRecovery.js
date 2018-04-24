import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import handleInputChange from '../shared/handleInputChange';
import captcha from '../shared/captcha';
import msgbox from '../shared/msgbox';
import ajax from '../shared/ajax';


class PasswordRecovery extends Component {
  constructor(props) {
    super(props);
    this.state = {
      email: "",
      captchaToken: "",
    };
    this.handleInputChange = handleInputChange.bind(this);
    this.send = this.send.bind(this);
    this.handleCaptchaSuccess = this.handleCaptchaSuccess.bind(this);
    this.captchaReferenceObserver = this.captchaReferenceObserver.bind(this);
  }

  handleCaptchaSuccess(token) {
    this.setState({
      captchaToken: token
    });
  }

  captchaReferenceObserver(captchaReference) {
    this.captcha = captchaReference;
  }

  send(event) {
    event.preventDefault();
    ajax.exec("password-recovery", "POST", this.state, event.target)
      .then(() => {
          msgbox.alert("If the provided address corresponds to a registered user you " +
                       "will shortly receive a message with your new password. " +
                       "If you don't receive anything in the next few minutes please " +
                       "contact us.").then(() => {
            this.props.history.push("/");
          });
      })
      .catch(() => {
          this.captcha.reset();
          this.setState({
              captchaToken: null
          });
      });
  }

  render() {
    return (
      <div className="container-fluid mintax-login-container">
        <div className="mintax-login-panel panel panel-default">
          <div className="panel-heading"><strong>MinTax</strong> for business travellers</div>
          <div className="panel-body">
            <form onSubmit={this.send}>
              <div className="form-group">
                <h4>Password Recovery</h4>
              </div>
              <div className="form-group">
                <input type="text" name="email" value={this.state.email} onChange={this.handleInputChange}
                      className="form-control" placeholder="E-mail" />
              </div>
              <div className="form-group">
                  {captcha.createComponent(this.handleCaptchaSuccess, this.captchaReferenceObserver)}
              </div>
              <p className="mintax-button-group">
                <Link to="/login" className="btn btn-default">Cancel</Link>
                <button className="btn btn-default" disabled={!this.state.captchaToken}>Reset Password</button>
                <span className="mintax-ajax-indicator" />
              </p>
            </form>
          </div>
        </div>
      </div>
    );
  }
}

export default PasswordRecovery;
