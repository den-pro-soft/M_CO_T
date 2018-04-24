import React, { Component } from 'react';
import MaskedInput from 'react-text-mask';


class PAYEInput extends Component {
  render() {
    return (
        <MaskedInput {...this.props} showMask={true} placeholderChar=" "
                    mask={[ /\d/, /\d/, /\d/, '/', /[A-Za-z0-9]/, /[A-Za-z0-9]/, /[A-Za-z0-9]/, /[A-Za-z0-9]/,
                                                    /[A-Za-z0-9]/, /[A-Za-z0-9]/, /[A-Za-z0-9]/, /[A-Za-z0-9]/,
                                                    /[A-Za-z0-9]/, /[A-Za-z0-9]/, /[A-Za-z0-9]/, /[A-Za-z0-9]/ ]}
                    pipe={value => value ? value.trim().toUpperCase() : value} />
    );
  }
}

export default PAYEInput;
