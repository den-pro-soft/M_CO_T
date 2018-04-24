import React, { Component } from 'react';
import { Route, Redirect, Switch } from 'react-router-dom';
import './Main.css';
import ajax from '../shared/ajax';
import AjaxError from './AjaxError';
import NavBar from './NavBar';
import Breadcrumb from './Breadcrumb';
import Company from './Company';
import Employees from './Employees';
import Assumptions from './Assumptions';
import DataUpload from './DataUpload';
import PreviousUploads from './PreviousUploads';
import Settings from './Settings';
import AdminCustomers from './AdminCustomers';
import AdminCustomerForm from './AdminCustomerForm';
import AdminUsers from './AdminUsers';
import AdminUserForm from './AdminUserForm';
import ReportResults from './ReportResults';
import AdditionalClarifications from './AdditionalClarifications';


class Main extends Component {
  constructor(props) {
      super(props);
      this.state = {
          accountInfo: undefined,
      }
  }
  componentDidMount() {
      if (!ajax.authenticated()) {
          this.props.history.push("/login");
      } else {
          ajax.exec('login/info')
            .then(accountInfo => {
              this.setState({ accountInfo });
            })
            .catch(() => this.setState({ accountInfo: null }));
      }
  }
  render() {

    if (this.state.accountInfo === undefined) {
      return (
        <div className="container-fluid">
          <div className="mintax-body-wrapper">
            <p className="mintax-ajax-in-progress" />
          </div>
        </div>
      );
    } else if (this.state.accountInfo === null) {
      return (
        <div className="container-fluid">
          <div className="mintax-body-wrapper">
            <AjaxError />
          </div>
        </div>
      );
    }

    return (
        <div className="container-fluid">
            <NavBar accountInfo={this.state.accountInfo}/>
            <Breadcrumb />
            <div className="mintax-body-wrapper">
                <Switch>
                    <Route exact path="/" render={() => <Redirect to="/company" />} />
                    <Route path="/company" component={Company} />
                    <Route path="/uk-employees" component={Employees} />
                    <Route path="/traveller-data/data-upload" component={DataUpload} />
                    <Route path="/traveller-data/previous-uploads" component={PreviousUploads} />
                    <Route path="/assumptions" component={Assumptions} />
                    <Route path="/reports" component={ReportResults} />
                    <Route path="/clarifications" component={AdditionalClarifications} />
                    <Route path="/settings" component={() => <Settings accountInfo={this.state.accountInfo}/>} />
                    <Route exact path="/admin/customers" component={AdminCustomers} />
                    <Route path="/admin/customers/new" component={AdminCustomerForm} />
                    <Route path="/admin/customers/:customerId" component={AdminCustomerForm} />
                    <Route exact path="/admin/users" component={AdminUsers} />
                    <Route path="/admin/users/new" component={AdminUserForm} />
                    <Route path="/admin/users/:userId" component={AdminUserForm} />
                </Switch>
            </div>

        </div>
    );
  }
}

export default Main;
