import React, { Component } from 'react';
import moment from 'moment';
import Dropzone from 'react-dropzone';
import ajax from '../shared/ajax';
import numbers from '../shared/numbers';
import './FileUpload.css';


class FileUpload extends Component {
  constructor(props) {
    super(props);

    this.state = {
      operations: [],
    }

    this.onDrop = this.onDrop.bind(this);
  }

  reset() {
    this.setState({ operations: [] });
  }
  
  onDrop(acceptedFiles, rejectedFiles) {
    const operations = this.state.operations;
    const promises = [];
    for (const idx in acceptedFiles) {
      const file = acceptedFiles[idx];
      const data = new FormData();
      const id = numbers.guid()
      data.append('file', file);
      data.append('id', id);
      for (const key in this.props.extraData) {
        let value = this.props.extraData[key];
        if (value instanceof moment) {
          value = value.toISOString();
        }
        data.append(key, value);
      }
      const operation = {
        seq: operations.length,
        fileName: file.name,
        status: "pending"
      };
      operations.push(operation);
      this.setState({ operations });
      const eventSourceCloseHandler = ajax.subscribe('upload-progress-' + id, data => {
        operation.progress = data;
        this.setState({ operations });
      });
      const onProgress = event => {
        if (operation.progress && !operation.progress.client) {
          // the server already sent something, we shouldn't mess with that
          return;
        }
        if (event.lengthComputable) {
          const progress = event.loaded / event.total * 100.0;
          if (progress < 100) {
            operation.progress = { progress: progress, status: "Uploading...", client: true };
          } else {
            operation.progress = undefined;
          }
          this.setState({ operations });
        }
      };
      const promise = ajax.exec(this.props.to, 'POST', data, undefined, onProgress)
        .then(res => {
            eventSourceCloseHandler();
            operation.status = "success";
            operation.progress = undefined;
            this.setState({ operations });
            return res;
        }, e => {
          eventSourceCloseHandler();
          operation.status = "failure";
          operation.progress = undefined;
          this.setState({ operations });
          throw e;
      });
      
      promises.push(promise);
    }
    const onUploadStarted = this.props.onUploadStarted || (function(){});
    const onBatchCompleted = this.props.onBatchCompleted || (function(){});
    onUploadStarted();
    Promise.all(promises).then(onBatchCompleted);
  }

  renderOperationDescription(oper) {

    const descriptions = {
      "pending": "Uploading...",
      "success": "Upload successful. Press the Save button below to proceed.",
      "failure": "Failed to upload.",
    };

    let description = descriptions[oper.status];
    // can be overriden by async progress reports
    if (oper.progress && oper.progress.status) {
      description = oper.progress.status;
    }

    let percentDone = undefined; // 0-100
    if (oper.progress && oper.progress.progress) {
      percentDone = Math.floor(oper.progress.progress);
    }

    return (
      <div>
        {oper.status == "pending" ? (
          <div className="progress pull-left">
            <div className="progress-bar-warning progress-bar-striped active" role="progressbar" aria-valuenow={percentDone}
                  aria-valuemin="0" aria-valuemax="100" style={{minWidth: "2.5em", width: (percentDone || 100) + "%"}}>
                {percentDone ? percentDone + "%" : "Please wait..."}
            </div>
          </div>
        ) : <span />}
        {description}
      </div>
    );
  }

  render() {
    let extraStyle = "";
    let results;
    if (this.props.minimal) {
      extraStyle += " mintax-dropzone-minimal";
      if (this.state.operations.length > 0) {
        const oper = this.state.operations[this.state.operations.length - 1];
        results = (
          <span className={"mintax-dropzone-result-" + oper.status}>
            {this.renderOperationDescription(oper)}
          </span>
        );
      } else {
        results = <span />;
      }
    } else {
      results = (
        <ul className="mintax-dropzone-results">
          {this.state.operations.map(oper => 
            <li key={oper.seq} className={"mintax-dropzone-result-" + oper.status}>
              {this.renderOperationDescription(oper)}
            </li>)}
        </ul>
      );
    }
    return (
      <div className={"mintax-dropzone noselect" + extraStyle}>
        <Dropzone ref={this.props.dropzoneRef} onDrop={this.onDrop}>
            Drag and drop to upload (you may also click here to open a file dialog)
        </Dropzone>
        {results}
      </div>
    );
  }
}

export default FileUpload;
