import React, { Component } from 'react';
import PropTypes from 'prop-types';


class UnsavedDataHandler extends Component {
  componentDidMount() {
    this.context.unsavedDataVerifiers.push(this.props.verifier);
  }
  componentWillUnmount() {
    const verifiers = this.context.unsavedDataVerifiers;
    verifiers.splice(verifiers.indexOf(this.props.verifier), 1);
  }
  render() {
      return null;
  }
};

UnsavedDataHandler.contextTypes = {
    unsavedDataVerifiers: PropTypes.array,
};

export default UnsavedDataHandler;
