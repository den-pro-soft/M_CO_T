import React from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';
import msgbox from '../shared/msgbox';


// https://stackoverflow.com/questions/34418254/is-there-a-way-using-react-router-to-set-an-active-class-on-the-wrapper-to-the-l
class NavLink extends React.Component {
  constructor(props) {
    super(props);
    this.confirmedNavigation = false;
    this.checkUnsavedData = this.checkUnsavedData.bind(this);
  }
  checkUnsavedData(event) {
    const target = event.target;
    let unsavedData = false;
    this.context.unsavedDataVerifiers.forEach(verifier => {
      if (verifier()) {
        unsavedData = true;
      }
    });
    if (unsavedData && !this.confirmedNavigation) {
      event.preventDefault();
      msgbox.confirm("Please note, the changes to this page have not been saved. Please click cancel to save the " +
                     "changes before proceeding. Alternatively, click OK if you are happy to proceed without saving the changes.",
                     "OK", "Cancel").then(() => {
        this.confirmedNavigation = true;
        target.click();
      });
    }
    this.confirmedNavigation = false;
  }
  render() {

    var isActive = this.context.router.route.location.pathname.match(new RegExp("^" + this.props.to + "(\/.*)?$"));
    var className = isActive ? 'active' : '';

    return(
      <li className={className}>
        <Link {...this.props} onClick={this.checkUnsavedData}>
          {this.props.children}
        </Link>
      </li>
    );
  }
}

NavLink.contextTypes = {
    router: PropTypes.object,
    unsavedDataVerifiers: PropTypes.array,
};

export default NavLink;
