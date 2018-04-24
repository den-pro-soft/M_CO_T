import React, { Component } from 'react';
import UnsavedDataHandler from './UnsavedDataHandler';
import _ from 'lodash';
import numbers from '../shared/numbers';
import ajax from '../shared/ajax';
import msgbox from '../shared/msgbox';
import redirectTo from '../shared/redirectTo';
import Scrollbars from './Scrollbars';
import AjaxError from './AjaxError';
import './Assumptions.css';


class Assumptions extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeTab: 'traveller-data',
      data: undefined,
      editing: false,
    };
    this.pristineData = _.cloneDeep(this.state.data);
    this.handleDataInputChange = this.handleDataInputChange.bind(this);
    this.send = this.send.bind(this);
    this.edit = this.edit.bind(this);
  }

  componentDidMount() {
    this.fetchData();
  }

  fetchData() {
    ajax.exec('assumptions')
      .then(data => {
        if (!data) {
          data = {
            outboundFromUKWithoutInbound: '1',
            businessTravellersTreaty3159: '1',
            businessTravellersTreaty60183: '1',
            useDeminimusIncidentalWorkdays: 'N',
            deminimusIncidentalWorkdays: '1',
            useDeminimusEEAA1Workdays: 'Y',
            deminimusEEAA1Workdays: '60',
            inboundToUKWithoutOutbound: '1',
          };
        }
        this.pristineData = _.cloneDeep(data);
        this.setState({ data });
      })
      .catch(() => {
        this.setState({ data: null });
      });
  }

  send(event) {
    event.preventDefault();
    const data = this.state.data;
    ajax.exec('assumptions', 'PUT', data, event.target).then(() => {
      msgbox.alert("Your assumptions settings have been successfully saved.").then(() => {
        redirectTo('/reports');
      });
    });
  }

  edit(event) {
    event.preventDefault();
    this.setState({ editing: true });
  }

  handleDataInputChange(fieldName, event) {
    const target = event.target;
    const type = target.type;
    const data = this.state.data;
    data[fieldName] = type === 'checkbox' ? target.checked : target.value;
    this.setState({ data });
  }

  renderTravellerDataTab() {
    return [
      <div className="form-group" key="traveller-data-question-1">
        <label>1. If there is an outbound flight from the UK but no corresponding inbound flight to the UK.</label>
        <div className="radio">
          <label>
            <input type="radio" name="outboundFromUKWithoutInbound" 
                   checked={this.state.data.outboundFromUKWithoutInbound === '1'}
                   disabled={!this.state.editing}
                   onChange={e => this.handleDataInputChange('outboundFromUKWithoutInbound', e)} value="1" />
            {' '}Assume that the inbound flight was taken at the start of the UK tax year i.e. 6 April
          </label>{' '}
        </div>
        <div className="radio">
          <label>
            <input type="radio" name="outboundFromUKWithoutInbound"
                   checked={this.state.data.outboundFromUKWithoutInbound === '2'}
                   disabled={!this.state.editing}
                   onChange={e => this.handleDataInputChange('outboundFromUKWithoutInbound', e)} value="2" />
            {' '}Assume that the inbound flight was taken at the start of the relevant tax month
          </label>
        </div>
        <div className="radio">
          <label>
            <input type="radio" name="outboundFromUKWithoutInbound"
                   checked={this.state.data.outboundFromUKWithoutInbound === '3'}
                   disabled={!this.state.editing}
                   onChange={e => this.handleDataInputChange('outboundFromUKWithoutInbound', e)} value="3" />
            {' '}Assume that the inbound flight was taken on the same day as the outbound flight
          </label>
        </div>
      </div>,
      <div className="form-group" key="traveller-data-question-2">
        <label>2. If there is an inbound flight to the UK but no corresponding outbound flight from the UK.</label>
        <div className="radio">
          <label>
            <input type="radio" name="inboundToUKWithoutOutbound"
                  checked={this.state.data.inboundToUKWithoutOutbound === '1'}
                  disabled={!this.state.editing}
                  onChange={e => this.handleDataInputChange('inboundToUKWithoutOutbound', e)} value="1" />
            {' '}Assume the individual was in the UK until the next outbound flight/trip taken irrespective of country of departure
          </label>{' '}
        </div>
        <div className="radio">
          <label>
            <input type="radio" name="inboundToUKWithoutOutbound"
                  checked={this.state.data.inboundToUKWithoutOutbound === '2'}
                  disabled={!this.state.editing}
                  onChange={e => this.handleDataInputChange('inboundToUKWithoutOutbound', e)} value="2" />
            {' '}Assume that the outbound flight was taken at the end of the UK tax year
          </label>
        </div>
      </div>
    ];
  }

  renderAppendix4Tab() {
    return [
      <div className="form-group" key="appendix-4-question-1">
        <label>3. For all business travellers from treaty countries spending 31 – 59 days in the UK.</label>
        <div className="radio">
          <label>
            <input type="radio" name="businessTravellersTreaty3159" 
                   checked={this.state.data.businessTravellersTreaty3159 === '1'}
                   disabled={!this.state.editing}
                   onChange={e => this.handleDataInputChange('businessTravellersTreaty3159', e)} value="1" />
            {' '}Automatically assume that none of these business travellers have a UK contract of 
            employment and the time spent in the UK does not form part of a more substantial period
          </label>{' '}
        </div>
        <div className="radio">
          <label>
            <input type="radio" name="businessTravellersTreaty3159"
                   checked={this.state.data.businessTravellersTreaty3159 === '2'}
                   disabled={!this.state.editing}
                   onChange={e => this.handleDataInputChange('businessTravellersTreaty3159', e)} value="2" />
            {' '}Do not make this assumption and instead confirm on an individual traveller basis
          </label>
        </div>
      </div>,
      <div className="form-group" key="appendix-4-question-2">
        <label>4. For all business travellers from treaty countries spending 60 – 183 days in the UK.</label>
        <div className="radio">
          <label>
            <input type="radio" name="businessTravellersTreaty60183" 
                   checked={this.state.data.businessTravellersTreaty60183 === '1'}
                   disabled={!this.state.editing}
                   onChange={e => this.handleDataInputChange('businessTravellersTreaty60183', e)} value="1" />
            {' '}Automatically assume that the UK company does not ultimately bear the cost of the
            employee’s remuneration; and the UK Company does not function as the employee’s employer
            during the UK assignment.
          </label>{' '}
        </div>
        <div className="radio">
          <label>
            <input type="radio" name="businessTravellersTreaty60183"
                   checked={this.state.data.businessTravellersTreaty60183 === '2'}
                   disabled={!this.state.editing}
                   onChange={e => this.handleDataInputChange('businessTravellersTreaty60183', e)} value="2" />
            {' '}Do not make this assumption and instead confirm on an individual traveller basis
          </label>
        </div>
      </div>
    ];
  }

  renderMerelyIncidentalDutiesTab() {
    return [
      <div className="form-group" key="merely-incidental-question-1">
        <label>5. For Non-Treaty/Branch visitors, please confirm if the Company would like to set a de-minimus
        threshold below which any UK workdays are considered to be merely incidental to their overseas duties?</label>
        <div className="row">
          <div className="col-xs-3 col-sm-2 col-md-1">
            <div className="radio">
              <label>
                <input type="radio" name="useDeminimusIncidentalWorkdays"
                      checked={this.state.data.useDeminimusIncidentalWorkdays === 'Y'}
                      disabled={!this.state.editing}
                      onChange={e => this.handleDataInputChange('useDeminimusIncidentalWorkdays', e)} value="Y" />
                {' '}Yes
              </label>
            </div>
          </div>
          <div className="col-xs-9 col-sm-10 col-md-11">
            <select id="deminimusIncidentalWorkdays" className="form-control mintax-small-field"
                    value={this.state.data.deminimusIncidentalWorkdays}
                    disabled={!this.state.editing || this.state.data.useDeminimusIncidentalWorkdays === 'N'}
                    onChange={(e) => this.handleDataInputChange('deminimusIncidentalWorkdays', e)}>
                {numbers.range(31).slice(1).map(n => <option key={n} value={n}>{n} {n > 1 ? "days" : "day"}</option>)}
            </select>
          </div>
          <div className="col-xs-12">
            <div className="radio">
              <label>
                <input type="radio" name="useDeminimusIncidentalWorkdays"
                      checked={this.state.data.useDeminimusIncidentalWorkdays === 'N'}
                      disabled={!this.state.editing}
                      onChange={e => this.handleDataInputChange('useDeminimusIncidentalWorkdays', e)} value="N" />
                {' '}No
              </label>
            </div>
          </div>
        </div>
      </div>
    ];
  }

  renderSocialSecurityTab() {
    return [
      <div className="form-group" key="social-security-question-1">
        <label>6. For business travellers from EEA countries (incl Switzerland) and reciprocal agreement countries,
        please confirm if the Company would like to set a de-minimus threshold above which the Company will apply
        for an A1 (Certificate of Coverage) from the home country?</label>
        <div className="row">
          <div className="col-xs-3 col-sm-2 col-md-1">
            <div className="radio">
              <label>
                <input type="radio" name="useDeminimusEEAA1Workdays"
                      checked={this.state.data.useDeminimusEEAA1Workdays === 'Y'}
                      disabled={!this.state.editing}
                      onChange={e => this.handleDataInputChange('useDeminimusEEAA1Workdays', e)} value="Y" />
                {' '}Yes
              </label>
            </div>
          </div>
          <div className="col-xs-9 col-sm-10 col-md-11">
            <select id="deminimusEEAA1Workdays" className="form-control mintax-small-field"
                    value={this.state.data.deminimusEEAA1Workdays}
                    disabled={!this.state.editing || this.state.data.useDeminimusEEAA1Workdays === 'N'}
                    onChange={(e) => this.handleDataInputChange('deminimusEEAA1Workdays', e)}>
                {numbers.range(61).slice(1).map(n => <option key={n} value={n}>{n} {n > 1 ? "days" : "day"}</option>)}
            </select>
          </div>
          <div className="col-xs-12">
            <div className="radio">
              <label>
                <input type="radio" name="useDeminimusEEAA1Workdays" 
                      checked={this.state.data.useDeminimusEEAA1Workdays === 'N'}
                      disabled={!this.state.editing}
                      onChange={e => this.handleDataInputChange('useDeminimusEEAA1Workdays', e)} value="N" />
                {' '}No
              </label>
            </div>
          </div>
        </div>
      </div>
    ];
  }

  renderTabContent() {
    switch (this.state.activeTab) {
      case 'traveller-data': return this.renderTravellerDataTab();
      case 'appendix-4': return this.renderAppendix4Tab();
      case 'merely-incidental-duties': return this.renderMerelyIncidentalDutiesTab();
      case 'social-security': return this.renderSocialSecurityTab();
      default: return <p>Unknown tab!</p>
    }
  }

  render() {

    if (this.state.data === undefined) {
      return <p className="mintax-ajax-in-progress" />;
    } else if (this.state.data === null) {
      return <AjaxError />
    }

    return (
      <form className="mintax-form" onSubmit={this.send}>
        <Scrollbars>
          <div className="mintax-form-body">
            <div className="row">
              <div className="col-xs-12 col-sm-3 col-md-3 col-lg-2">
                <ul className="nav nav-pills nav-stacked noselect">
                  <li className={this.state.activeTab == 'traveller-data' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'traveller-data' })}>Traveller Data</a>
                  </li>
                  <li className={this.state.activeTab == 'appendix-4' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'appendix-4' })}>Appendix 4</a>
                  </li>
                  <li className={this.state.activeTab == 'merely-incidental-duties' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'merely-incidental-duties' })}>Merely Incidental Duties</a>
                  </li>
                  <li className={this.state.activeTab == 'social-security' ? 'active' : ''}>
                      <a onClick={() => this.setState({ activeTab: 'social-security' })}>Social Security</a>
                  </li>
                </ul>
              </div>
              <div className="col-xs-12 col-sm-8 col-md-9 col-lg-10">
                {this.renderTabContent()}
              </div>
            </div>
          </div>
        </Scrollbars>
        <div className="mintax-form-footer">
          <div className="mintax-button-group-right">
            { this.state.editing ? 
                <button className="btn btn-primary">Save</button> :
                <button className="btn btn-primary" type="button" onClick={this.edit}>Edit</button> }
            <span className="mintax-ajax-indicator" />
          </div>
        </div>
        <UnsavedDataHandler verifier={() => !_.isEqual(this.pristineData, this.state.data)} />
      </form>
    );
  }
}

export default Assumptions;
