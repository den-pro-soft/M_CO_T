import React, { Component } from 'react';
import './Header.css';


class Header extends Component {
  render() {
    return (
      <div className="mintax-header noselect">
        <div className="mintax-brand">
          <span>
            <span className="mintax-brand-appname">MinTax</span>{' '}
            <span className="mintax-brand-slogan hidden-xs">minimising your UK employment tax liabilities<span className="hidden-sm"> and risk</span></span>
          </span>
        </div>
        <div className="mintax-contactus">
          <a href="mailto:contactus@e-taxconsulting.com">contactus@e-taxconsulting.com</a>
          <span><span className="glyphicon glyphicon-earphone" /> + 44(0) 77928 12038</span>
        </div>
      </div>
    );
  }
}

export default Header;
