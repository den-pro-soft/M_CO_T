import React, { Component } from 'react';
import _ from 'lodash';
import DatePicker from 'react-datepicker';
import './DatePickerInput.css';


class DatePickerInput extends Component {
  render() {
    const cascadedProps = _.clone(this.props);
    delete cascadedProps.onChange;
    return <DatePicker {...this.props}
                       onChange={value => {
                         if (this.props.onChange) {
                           this.props.onChange(value ? value.format('YYYY-MM-DD') : null);
                         }
                       }}
                       dateFormat="DD/MM/YYYY" />;
  }
}

export default DatePickerInput;
