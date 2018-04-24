import React, { Component } from 'react';


class AjaxError extends Component {
  render() {
    return (
      <p className="mintax-ajax-error">Unable to load, please refresh the page. If the problem persists please contact us.</p>
    );
  }
}

export default AjaxError;
