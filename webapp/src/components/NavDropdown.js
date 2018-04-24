import React from 'react';
import PropTypes from 'prop-types';


// https://stackoverflow.com/questions/34418254/is-there-a-way-using-react-router-to-set-an-active-class-on-the-wrapper-to-the-l
class NavDropdown extends React.Component {
  render() {
    
    var isActive = this.context.router.route.location.pathname.match(new RegExp("^" + this.props.for + "(\/.*)?$"));
    var className = isActive ? 'dropdown active' : 'dropdown';

    return(
      <li className={className}>
        <a href="#" className="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
            {this.props.title} <span className="caret"></span>
        </a>
        <ul className="dropdown-menu">
          {this.props.children}
        </ul>
      </li>
    );
  }
}

NavDropdown.contextTypes = {
    router: PropTypes.object
};

export default NavDropdown;
