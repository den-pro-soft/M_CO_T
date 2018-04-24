import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import './App.css';
import NavLink from './NavLink';
import Header from './Header';
import Footer from './Footer';
import Login from './Login';
import PasswordRecovery from './PasswordRecovery';
import Main from './Main';


class App extends Component {
  getChildContext() {
    return {
      unsavedDataVerifiers: [],
    };
  }
  render() {
    return (
      <div className="mintax-app">
        <Header />
        <Router>
          <Switch>
            <Route path="/login" component={Login} />
            <Route path="/password-recovery" component={PasswordRecovery} />
            <Route component={Main} />
          </Switch>
        </Router>
        <Footer />
      </div>
    );
  }
}

App.childContextTypes = {
  unsavedDataVerifiers: PropTypes.array,
};

export default App;
