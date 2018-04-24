import moment from 'moment';


export default {

    parse(value) {
        if (!value) {
            return null;
        }
        let date = moment(value, [ moment.ISO_8601, "DD/MM/YYYY" ]);
        if (!date.isValid()) {
            return null;
        }
        return date;
    },

    format(value, pattern) {
        let date = this.parse(value);
        if (!date) {
            return "";
        }
        return date.format(pattern);
    },

    formatDateTime(value) {
        return this.format(value, "DD/MM/YYYY HH:mm");
    },

    formatDate(value) {
        return this.format(value, "DD/MM/YYYY");
    },

    getTaxYearsFrom(from, to) {
        // we need to have a from date
        if (typeof from === 'string' && from.length < 10) {
            return [ undefined ];
        }
        // parsing to get moment objects
        const fromDate = this.parse(from);
        const toDate = this.parse(to);
        // if invalid from date
        // then we return undefined
        if (!fromDate) {
            return [ undefined ];
        }
        const taxYears = [];
        const year = fromDate.year();
        // the user probably is typing the year right now
        if (year < 1900) {
            return [ undefined ];
        }
        const month = fromDate.month(); // 0-based
        const dom = fromDate.date();
        const taxYearFirstMonth = 3;
        const taxYearFirstDay = 6;
        let auxTaxYear;
        // lets identify the first tax year
        if (month < taxYearFirstMonth || (month == taxYearFirstMonth && dom < taxYearFirstDay)) {
            auxTaxYear = year - 1;
        } else {
            auxTaxYear = year;
        }
        taxYears.push(auxTaxYear);
        // if we have a to date, we need to check
        // if latter tax years are included
        if (toDate) {
            auxTaxYear++;
            while (moment().year(auxTaxYear)
                           .month(taxYearFirstMonth)
                           .date(taxYearFirstDay)
                           .startOf('day')
                           .isSameOrBefore(toDate)) {
                taxYears.push(auxTaxYear);
                auxTaxYear++;
            }
        }
        return taxYears;
    }

};
