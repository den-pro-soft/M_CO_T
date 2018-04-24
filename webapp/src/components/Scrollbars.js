import React from 'react';
import { Scrollbars as WrappedComponent } from 'react-custom-scrollbars';
import './Scrollbars.css';


class Scrollbars extends React.Component {
  render() {
    return(
        <WrappedComponent className="mintax-scrollable"
                renderTrackHorizontal={props => <div {...props} className="mintax-scrollable-track-horizontal"/>}
                renderTrackVertical={props => <div {...props} className="mintax-scrollable-track-vertical"/>}
                renderThumbHorizontal={props => <div {...props} className="mintax-scrollable-thumb-horizontal"/>}
                renderThumbVertical={props => <div {...props} className="mintax-scrollable-thumb-vertical"/>}
                renderView={props => <div {...props} className="mintax-scrollable-view"/>}>
            {this.props.children}
        </WrappedComponent>
    );
  }
}

export default Scrollbars;
