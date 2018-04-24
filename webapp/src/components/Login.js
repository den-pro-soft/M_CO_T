import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import handleInputChange from '../shared/handleInputChange';
import ajax from '../shared/ajax';
import captcha from '../shared/captcha';
import './Login.css';


class Login extends Component {
  constructor(props) {
    super(props);

    this.state = {
      email: "",
      password: "",
      captchaToken: "",
    };

    this.send = this.send.bind(this);
    this.handleInputChange = handleInputChange.bind(this);
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

      ajax.exec("login", "POST", this.state, event.target)
        .then(({ authToken }) => {
            localStorage.setItem("authTokenId", authToken);
            this.props.history.push("/");
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
                    <input type="text" name="email" value={this.state.email} onChange={this.handleInputChange}
                          className="form-control" placeholder="E-mail" />
                  </div>
                  <div className="form-group">
                    <input type="password" name="password" value={this.state.password} onChange={this.handleInputChange}
                          className="form-control" placeholder="Password" />
                  </div>
                  <div className="form-group">
                      {captcha.createComponent(this.handleCaptchaSuccess, this.captchaReferenceObserver)}
                  </div>
                  <p className="mintax-button-group">
                    <button className="btn btn-default" disabled={!this.state.captchaToken}>Sign In</button>
                    <span className="mintax-ajax-indicator" />
                  </p>
                  <p>
                    <Link to="/password-recovery">Forgot My Password</Link>
                  </p>
                </form>
              </div>
          </div>
        </div>
    );
  }
}

export default Login;
