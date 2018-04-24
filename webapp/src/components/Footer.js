import React, { Component } from 'react';
import './Footer.css';


class Footer extends Component {
  render() {
    return (
      <div className="mintax-footer noselect">
        <div className="mintax-about-etax"><a href="http://e-taxconsulting.com/">About E-Tax Consulting</a></div>
        <div className="mintax-copyright">© 2017 E-Tax Consulting Ltd</div>
      </div>
    );
  }
}

export default Footer;
