import React from 'react';
import { Route } from 'react-router-dom';
import './Breadcrumb.css';


class Breadcrumb extends React.Component {
  render() {
    return(
      <ol className="breadcrumb noselect">
        <li className="mintax-you-are-here">You are here:</li>
        <Route path="/company" component={() => <li>Company</li>} />
        <Route path="/uk-employees" component={() => <li>UK Employees</li>} />
        <Route path="/traveller-data" component={() => <li>Traveller Data</li>} />
        <Route path="/traveller-data/data-upload" component={() => <li>Data Upload</li>} />
        <Route path="/traveller-data/previous-uploads" component={() => <li>Previous Uploads</li>} />
        <Route path="/assumptions" component={() => <li>Assumptions</li>} />
        <Route path="/clarifications" component={() => <li>Clarifications</li>} />
        <Route path="/reports" component={() => <li>Reports</li>} />
        <Route path="/in-year-actions" component={() => <li>In-Year Actions</li>} />
        <Route path="/in-year-actions/payroll-withholding" component={() => <li>Payroll withholding</li>} />
        <Route path="/in-year-actions/151-183-days-applications" component={() => <li>151 - 183 days applications</li>} />
        <Route path="/in-year-actions/certificates-of-coverage" component={() => <li>Certificates of Coverage</li>} />
        <Route path="/in-year-actions/tax-residence-certificates" component={() => <li>Tax Residence Certificates</li>} />
        <Route path="/annual-returns" component={() => <li>Annual Returns</li>} />
        <Route path="/annual-returns/simplified-payroll" component={() => <li>Simplified payroll</li>} />
        <Route path="/annual-returns/appendix-4" component={() => <li>Appendix 4</li>} />
        <Route path="/non-uk-travel" component={() => <li>Non-UK Travel</li>} />
        <Route path="/settings" component={() => <li>Settings</li>} />
        <Route path="/admin" component={() => <li>Administration Panel</li>} />
        <Route path="/admin/customers" component={() => <li>Customers</li>} />
        <Route path="/admin/users" component={() => <li>Users</li>} />
      </ol>
    );
  }
}

export default Breadcrumb;
