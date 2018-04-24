import React from 'react';


const PAGE_SIZE = 50;


class PagingControls extends React.Component {

    static getPagedResults(filteredResults, currentPage) {
      const firstRecord = currentPage * PAGE_SIZE;
      return filteredResults.slice(firstRecord, firstRecord + PAGE_SIZE);
    }
    
    render() {
        const currentPage = this.props.currentPage;
        const pages = this.props.total / PAGE_SIZE;
        const lastPage = pages == Math.floor(pages) ? pages - 1 : Math.floor(pages);
        const firstIntervalButton = Math.max(0, Math.min(lastPage - 2, currentPage - 1));
        const intervalButtons = [];
        for (let i = firstIntervalButton; i <= Math.min(lastPage, firstIntervalButton + 2); i++) {
          const buttonClasses = i == currentPage ? "mintax-current-page" : "";
          intervalButtons.push((
            <a className={buttonClasses} key={i}
                    onClick={() => this.props.onPageClick(i)}>
              {i * PAGE_SIZE + 1}-{Math.min(this.props.total, i * PAGE_SIZE + PAGE_SIZE)}
            </a>
          ));
          intervalButtons.push(' ');
        }
        return (
          <div className="mintax-pagination">
            <a className={ currentPage == 0 ? "mintax-disabled" : "" }
                    onClick={() => this.props.onPageClick(0)}>First Page</a>{' '}
            <a className={ currentPage == 0 ? "mintax-disabled" : "" }
                    onClick={() => this.props.onPageClick(Math.max(0, currentPage - 1))}>Previous</a>{' '}
            {intervalButtons}
            <a className={ currentPage == lastPage ? "mintax-disabled" : "" }
                    onClick={() => this.props.onPageClick(Math.min(lastPage, currentPage + 1))}>Next</a>{' '}
            <a className={ currentPage == lastPage ? "mintax-disabled" : "" }
                    onClick={() => this.props.onPageClick(lastPage)}>Last Page</a>
          </div>
        );
    }
}

export default PagingControls;
