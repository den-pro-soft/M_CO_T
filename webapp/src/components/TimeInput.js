import React, { Component } from 'react';
import MaskedInput from 'react-text-mask';


class TimeInput extends Component {
  render() {
    return (
        <MaskedInput {...this.props} showMask={true} placeholderChar=" "
                    mask={[ /\d/, /\d/, ':', /\d/, /\d/ ]}
                    pipe={value => value ? value.trim().toUpperCase() : value} />
    );
  }
}

export default TimeInput;
