"""Company data REST resource"""

from uuid import uuid4
from collections import defaultdict
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from error_handling import InvalidUsage
import security
import validation as val
from models.storage import db
from models.companies_infos import CompaniesInfo
from models.companies import Company
from models.branches import Branch
# pylint: disable=C0103
bp = Blueprint('company', __name__)


@bp.route('', methods=['GET'])
def fetch():
    """Fetches company data"""
    user = security.authorize(request)

    companies_info = CompaniesInfo.query.filter_by(customer_id=user.customer.id).first()
    if companies_info is None:
        return jsonify(None)

    companies = Company.query.options(joinedload('branches')) \
                       .filter_by(customer_id=user.customer.id).all()
    companies_json = []
    for company in companies:
        branches_json = []
        for branch in company.branches:
            branches_json.append({
                "name": branch.name,
                "country": branch.country,
            })
        companies_json.append({
            "name": company.name,
            "paye": company.paye,
            "trackingMethod": company.tracking_method,
            "otherTrackingMethod": company.other_tracking_method,
            "numberOfBranches": len(company.branches),
            "branches": branches_json,
            "simplifiedPayroll": company.simplified_payroll,
            "simplifiedPayrollPaye": company.simplified_payroll_paye,
        })

    return jsonify({
        "numberOfCompanies": len(companies),
        "branchesOverseas": 'Y' if companies_info.branches_overseas else 'N',
        "companies": companies_json,
        "simplifiedAnnualPayroll": 'Y' if companies_info.simplified_annual_payroll else 'N',
        "employeesOnAssignmentUK": 'Y' if companies_info.employees_on_assignment_uk else 'N',
        "anyNonTaxableEmployees": 'Y' if companies_info.any_non_taxable_employees else 'N',
    })


@bp.route('', methods=['PUT'])
def update():
    """Receives company data and stores in the database"""
    user = security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_input(data)

    CompaniesInfo.query.filter_by(customer_id=user.customer.id).delete()
    # the below instruction cascades automatically to branches
    Company.query.filter_by(customer_id=user.customer.id).delete()

    companies_info = CompaniesInfo(user.customer.id,
                                   data['branchesOverseas'] == 'Y',
                                   data['simplifiedAnnualPayroll'] == 'Y',
                                   data['employeesOnAssignmentUK'] == 'Y',
                                   data['anyNonTaxableEmployees'] == 'Y')
    db.session.add(companies_info)

    if 'companies' in data and isinstance(data['companies'], list):
        for company_data in data['companies']:
            company_id = uuid4()
            company = Company(company_id,
                              user.customer.id,
                              company_data['name'],
                              company_data['paye'],
                              company_data['trackingMethod'],
                              company_data['otherTrackingMethod'],
                              company_data['simplifiedPayroll'],
                              company_data['simplifiedPayrollPaye'])
            if data['branchesOverseas'] == 'Y':
                for branch_data in company_data['branches']:
                    branch = Branch(uuid4(),
                                    company_id,
                                    branch_data['name'],
                                    branch_data['country'])
                    company.branches.append(branch)
            db.session.add(company)

    db.session.commit()

    return ('', 204)


def check_input(data):
    """Check the validity of input data"""
    errors = []

    # question 1
    if 'numberOfCompanies' not in data \
            or data['numberOfCompanies'] is None \
            or data['numberOfCompanies'] == '':
        errors.append('Question 1: Number of companies is required')
    else:
        val.check_posi_integer(errors, data['numberOfCompanies'],
                               'Question 1: Number of companies')

    # question 2
    if 'branchesOverseas' not in data or data['branchesOverseas'] is None:
        errors.append('Question 2: Please provide an answer')
    elif data['branchesOverseas'] not in ['Y', 'N']:
        errors.append('Question 2: Invalid boolean answer')

    # question 3
    check_question3_branch_count(errors, data)
    check_question3_companies(errors, data)
    check_question3_duplicated_paye(errors, data)
    check_question3_spr_company_count(errors, data)

    # question 4
    simplified_annual_payroll = False
    if 'simplifiedAnnualPayroll' not in data or data['simplifiedAnnualPayroll'] is None:
        errors.append('Question 4: Please provide an answer')
    elif data['simplifiedAnnualPayroll'] not in ['Y', 'N']:
        errors.append('Question 4: Invalid boolean answer')
    elif data['simplifiedAnnualPayroll'] == 'Y':
        simplified_annual_payroll = True

    # question 5/6
    question_number = 6 if simplified_annual_payroll else 5
    if 'employeesOnAssignmentUK' not in data or data['employeesOnAssignmentUK'] is None:
        errors.append('Question {0}: Please provide an answer'.format(question_number))
    elif data['employeesOnAssignmentUK'] not in ['Y', 'N']:
        errors.append('Question {0}: Invalid boolean answer'.format(question_number))

    # question 6/7
    question_number = question_number + 1
    if 'anyNonTaxableEmployees' not in data or data['anyNonTaxableEmployees'] is None:
        errors.append('Question {0}: Please provide an answer'.format(question_number))
    elif data['anyNonTaxableEmployees'] not in ['Y', 'N']:
        errors.append('Question {0}: Invalid boolean answer'.format(question_number))

    if errors:
        raise InvalidUsage(errors)


def check_question3_branch_count(errors, data):
    """Check if there is at least one branch if
    question 2 answer is 'YES'"""
    branches_overseas = 'branchesOverseas' in data and data['branchesOverseas'] == 'Y'
    if branches_overseas:
        branch_count = 0
        if 'companies' in data and isinstance(data['companies'], list):
            for company in data['companies']:
                if 'branches' in company and isinstance(company['branches'], list):
                    branch_count += len(company['branches'])
        if branch_count == 0:
            errors.append('Question 3: Specify at least 1 branch or change ' +
                          'your answer to question 2')


def check_question3_spr_company_count(errors, data):
    """Check if there is at least one company
    marked as Simplified Payroll if question 4
    answer is 'YES'"""
    spr_key = 'simplifiedAnnualPayroll'
    simplified_annual_payroll = spr_key in data and data[spr_key] == 'Y'
    if simplified_annual_payroll:
        spr_company_count = 0
        if 'companies' in data and isinstance(data['companies'], list):
            for company in data['companies']:
                sp_key = 'simplifiedPayroll'
                if sp_key in company and company[sp_key]:
                    spr_company_count += 1
        if spr_company_count == 0:
            errors.append("Question 3: Mark at least 1 company as operating " +
                          "with a Simplified Payroll or change your answer to question 4")


def check_question3_companies(errors, data):
    """Check question 3 input data"""
    spr_key = 'simplifiedAnnualPayroll'
    simplified_annual_payroll = spr_key in data and data[spr_key] == 'Y'
    if 'companies' in data and isinstance(data['companies'], list):
        for idx, company in enumerate(data['companies']):
            check_question3_company(errors, data, idx, company, simplified_annual_payroll)


def check_question3_company(errors, data, idx, company, simplified_annual_payroll):
    """Check a single company from question 3"""
    error_prefix = 'Question 3 - Company #{0}:'.format(idx + 1)
    if 'name' not in company or not company['name']:
        errors.append(error_prefix + ' name is required')
    elif len(company['name']) > 50:
        errors.append(error_prefix + ' name must have less than or exactly 50 characters')

    if 'paye' not in company or not company['paye']:
        errors.append(error_prefix + ' PAYE reference is required')
    else:
        val.check_paye_reference(errors, company['paye'], error_prefix)

    if 'trackingMethod' not in company or not company['trackingMethod']:
        errors.append(error_prefix + ' Tracking method is required')
    elif company['trackingMethod'] not in ['1', '2', '3', '4']:
        errors.append(error_prefix + ' invalid tracking method')
    elif company['trackingMethod'] == '4': # Other
        if 'otherTrackingMethod' not in company or not company['otherTrackingMethod']:
            errors.append(error_prefix + ' please describe the tracking method')
        elif len(company['otherTrackingMethod']) > 50:
            errors.append(error_prefix + ' Tracking method description must have' + \
                                         ' less than or exactly 50 characters')

    branches_overseas = 'branchesOverseas' in data and data['branchesOverseas'] == 'Y'
    if  branches_overseas:
        check_question3_company_branches(errors, idx, company)

    check_question5_company_simpl_payr(errors, company, simplified_annual_payroll, error_prefix)


def check_question3_duplicated_paye(errors, data):
    """Checks if any duplicated PAYE References"""
    paye_count = defaultdict(int)
    error_template = 'Question 3: There are {0} companies with the PAYE Reference "{1}"'
    if 'companies' in data and isinstance(data['companies'], list):
        for company in data['companies']:
            paye_count[company['paye']] += 1
    for paye, count in paye_count.items():
        if val.PAYE_REGEX.match(paye) and count > 1:
            errors.append(error_template.format(count, paye))


def check_question5_company_simpl_payr(errors, company, simplified_annual_payroll, error_prefix):
    """Check a single company question 5 answers"""
    if simplified_annual_payroll:
        sp_key = 'simplifiedPayroll'
        if sp_key in company and company[sp_key]:
            if 'simplifiedPayrollPaye' not in company or not company['simplifiedPayrollPaye']:
                errors.append(error_prefix + ' Simplified Payroll PAYE reference is required')
            else:
                val.check_paye_reference(errors, company['simplifiedPayrollPaye'], error_prefix)


def check_question3_company_branches(errors, company_idx, company):
    """Check a single question 3 company's branches"""
    if 'branches' in company and isinstance(company['branches'], list):
        for idx, branch in enumerate(company['branches']):
            check_question3_company_branch(errors, company_idx, idx, branch)


def check_question3_company_branch(errors, company_idx, idx, branch):
    """Check a single branch from a question 3 company"""
    error_prefix = 'Question 3 - Company #{0} - Branch #{1}:'.format(company_idx + 1, idx + 1)
    if 'name' not in branch or not branch['name']:
        errors.append(error_prefix + ' name is required')
    elif len(branch['name']) > 50:
        errors.append(error_prefix + ' name must have less than or exactly 50 characters')

    if 'country' not in branch or not branch['country']:
        errors.append(error_prefix + ' country is required')
