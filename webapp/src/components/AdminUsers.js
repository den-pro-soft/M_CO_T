import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import ajax from '../shared/ajax';
import dates from '../shared/dates';
import msgbox from '../shared/msgbox';
import handleInputChange from '../shared/handleInputChange';
import AjaxError from './AjaxError';
import Scrollbars from './Scrollbars';


class AdminUsers extends Component {
  constructor(props) {
    super(props);
    this.state = {
      users: undefined,
      filter: "",
      showDisabled: false,
    };
    this.handleInputChange = handleInputChange.bind(this);
  }

  componentDidMount() {
    this.fetchUsers();
  }

  fetchUsers() {
    ajax.exec('admin/users')
        .then(users => this.setState({ users }))
        .catch(() => this.setState({ users: null }));
  }

  deleteUser(user) {
    msgbox.confirm(`Do you really want to remove user '${user.firstName} ${user.secondName}'?`).then(() => {
      ajax.exec(`admin/users/${user.id}`, 'DELETE').then(() => {
        user.active = false;
        const users = this.state.users;
        this.setState({ users });
      })
    });
  }

  filteredUsers() {
    const users = this.state.users;
    const filter = this.state.filter.toLowerCase();
    const showDisabled = this.state.showDisabled;
    return this.state.users.filter(user => {
      const fullName = `${user.firstName} ${user.secondName}`.toLowerCase();
      const customerName = (user.customerName || "").toLowerCase();
      const email = (user.email || "").toLowerCase();
      const textFilter = fullName.indexOf(filter) >= 0 ||
        customerName.indexOf(filter) >= 0 ||
        email.indexOf(filter) >= 0;
      const activeFilter = showDisabled || user.active;
      return textFilter && activeFilter;
    });
  }

  render() {

    if (this.state.users === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.users === null) {
      return <AjaxError />
    }

    const filteredUsers = this.filteredUsers();

    return (
      <form className="mintax-form" onSubmit={this.send}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="form-group">
              <input className="form-control mintax-medium-field" placeholder="Filter"
                     value={this.state.filter} onChange={this.handleInputChange} name="filter" />
              <div className="checkbox">
                <label>
                  <input type="checkbox" checked={this.state.showDisabled}
                         onChange={this.handleInputChange} name="showDisabled" /> Show disabled user accounts
                </label>
              </div>
            </div>
            {filteredUsers.length > 0 ? (
              <div className="form-group">
                <table className="table table-bordered table-striped">
                  <thead>
                    <tr>
                      <th style={{ width: "250pt", minWidth: "125pt" }}>Full Name</th>
                      <th style={{ width: "250pt", minWidth: "125pt" }}>E-mail</th>
                      <th style={{ width: "250pt", minWidth: "125pt" }}>Customer Name</th>
                      <th className="mintax-actions-column"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map(user => (
                      <tr key={user.id} className={user.active ? "" : "mintax-inactive-row"}>
                          <td>{user.firstName} {user.secondName}</td>
                          <td>{user.email}</td>
                          <td>{user.customerName}</td>
                          <td className="mintax-actions-column">
                              <Link to={`/admin/users/${user.id}`} className="btn btn-sm btn-default"><i className="glyphicon glyphicon-pencil" /></Link>{' '}
                              {user.active ? (
                                <button type="button" className="btn btn-sm btn-default" onClick={() => this.deleteUser(user)}><i className="glyphicon glyphicon-trash" /></button>
                              ) : <span />}
                          </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>No records found</p>
            )}
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group-right">
            <Link to="/admin/users/new" className="btn btn-primary">New User</Link>
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
      </form>
    );
  }
}

export default AdminUsers;
