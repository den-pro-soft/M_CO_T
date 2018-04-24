import React from 'react';
import { Link } from 'react-router-dom';
import ajax from '../shared/ajax';
import redirectTo from '../shared/redirectTo';
import './NavBar.css';
import NavLink from './NavLink';
import NavDropdown from './NavDropdown';


class NavBar extends React.Component {

  logout() {
    ajax.logout().then(() => redirectTo("/login"));
  }
  
  render() {
    return(
      <nav className="navbar navbar-default mintax-topbar noselect">
        <div className="container-fluid">
            <div className="navbar-header">
                <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#mintax-navbar-collapse-1" aria-expanded="false">
                    <span className="sr-only">Toggle navigation</span>
                    <span className="icon-bar"></span>
                    <span className="icon-bar"></span>
                    <span className="icon-bar"></span>
                </button>
                <Link className="navbar-brand" to="/"><span className="glyphicon glyphicon-home" /></Link>
            </div>

            <div className="collapse navbar-collapse" id="mintax-navbar-collapse-1">
                <ul className="nav navbar-nav">
                    <NavLink to="/company">1. Company</NavLink>
                    <NavLink to="/uk-employees">2. UK Employees</NavLink>
                    <NavDropdown for="/traveller-data" title="3. Traveller Data">
                        <NavLink to="/traveller-data/data-upload">3.1. Data Upload</NavLink>
                        <NavLink to="/traveller-data/previous-uploads">3.2. Previous Uploads</NavLink>
                    </NavDropdown>
                    <NavLink to="/assumptions">4. Assumptions</NavLink>
                    <NavLink to="/reports">5. Reports</NavLink>
                    <NavLink to="/clarifications">6. Clarifications</NavLink>
                    <NavDropdown for="/in-year-actions" title="7. In-Year Actions">
                        <NavLink to="/in-year-actions/payroll-withholding">7.1. Payroll withholding</NavLink>
                        <NavLink to="/in-year-actions/151-183-days-applications">7.2. 151 - 183 days applications</NavLink>
                        <NavLink to="/in-year-actions/certificates-of-coverage">7.3. Certificates of Coverage</NavLink>
                        <NavLink to="/in-year-actions/tax-residence-certificates">7.4. Tax Residence Certificates</NavLink>
                    </NavDropdown>
                    <NavDropdown for="/annual-returns" title="8. Annual Returns">
                        <NavLink to="/annual-returns/simplified-payroll">8.1. Simplified Payroll</NavLink>
                        <NavLink to="/annual-returns/appendix-4">8.2. Appendix 4</NavLink>
                    </NavDropdown>
                    <NavDropdown for="/non-uk-travel" title="9. Non-UK Travel">
                        <NavLink to="/non-uk-travel/page-1">9.1. Page 1</NavLink>
                        <NavLink to="/non-uk-travel/page-2">9.2. Page 2</NavLink>
                    </NavDropdown>
                </ul>
                <ul className="nav navbar-nav navbar-right">
                    <li className="dropdown">
                        <a href="#" className="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">{this.props.accountInfo.firstName} <span className="caret"></span></a>
                        <ul className="dropdown-menu">
                            <NavLink to="/settings">Settings</NavLink>
                            {this.props.accountInfo.admin ?
                                <NavLink to="/admin/customers">Customers</NavLink> :
                                <span /> }
                            {this.props.accountInfo.admin ?
                                <NavLink to="/admin/users">Users</NavLink> :
                                <span /> }
                            <li><a style={{ cursor: "pointer" }} onClick={this.logout}>Sign out</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
      </nav>
    );
  }
}

export default NavBar;
