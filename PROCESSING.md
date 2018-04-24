# Processing

This file describes MinTax's data processing flow.

## Relevant entities

### Raw Employee Data (RED)

Each customer may or may not have an active `Employees` spreadsheet. Each employee present in this data source has the following attributes:

* Name
* ID
* Arrangements

The tuple (name, ID) identifies uniquely an employee. Arrangements is a collection of records defined by:

* Arrangement Category (UK Employee, UK Expatriate, Overseas Branch Employee, NT/STA)
* Effective From (optional)
* Effective To (optional)

### Raw Travel Data (RTD)

The client uploads multiple traveller data spreadsheets. Each one of them has zero or more trips in them. The most important fields of a trip are:

* Traveller Name/ID
* Employee Country
* Ticket Type
* Origin Country
* Destination Country
* Departure Date/Time
* Arrival Date/Time

Each record of this entity may have zero or more errors attached to it, eventually found while collecting the raw data from the spreadsheet. Examples of such
errors are invalid date/time syntax or invalid country name/3-letter code.

### Report Periods (RP)

Attached to each traveller data upload there is a date interval (period).

### Assumptions (APT)

The client may change some settings related to how the system should process the traveller data.

### Employees (EE)

This is a view derived from Raw Employee Data (RED). Consumers of this view can assume the following properties:

* There will be at most one employee with a given ID.
* In the event of multiple work arrangements, they will have valid effective from-to settings, in a way that no pair of arrangements overlap.

### Trips (TRP)

This is a view derived from Raw Travel Data (RTD). Consumers of this view can assume the following properties:

* Each trip will appear only once (trips found on multiple spreadsheets will be handled).
* There will only be trips crossing UK borders.
* There will not be trips with invalid data or with errors attached to it.
* Refund tickets will be ignored.

### Countries (CTR)

This data source provides country names and 3-letter codes.

### Treaty Country List (TCL)

This data source provides date intervals in which countries had a treaty signed with the UK for the purposes of this application.

### Employee Travel History (ETH)

This is a view derived from Employees (EE) and Trips (TRP). This entity has the following properties:

* Employee Name/ID
* From: Inclusive
* To: Inclusive (optional for at most one record)
* Report Category: Unknown, UK Employee/Expatriate, Overseas Branch Visitor, Non-Treaty Country Visitor, Treaty Country Visitor
* Unclear home country periods: time intervals where the employee home country is unclear. This is used in Additional Clarifications.

### Employee Home Country Clarifications (ECL)

Whenever the user clarifies an employee home country this information is sent again to the processing engine.

### Inbound Trip Assumptions Correct Dates (ICD)

Whenever the user provides a correct date for an assumed inbound trip this information is sent again to the processing engine.

### Border Cross Time Clarifications (BCT)

Whenever the user provides a correct time for conflicting trips (same employee, date, time, origin and destination) this
information is sent again to the processing engine.

### Report Results (RR)

This view is derived from Employee Travel History (ETH) and Report Periods (RP), and has the following properties:

* Report Period From/To
* Employee Name/ID
* Report Category
* UK Workdays

## Processing Snowball

Note that there is a dependency graph between the above entities:

```
RED*    ->    EE    -\

CTR*    -\           |-> ETH   ---> RR

RTD*    -|->  TRP   -|   RP*   -/

BCT*    -/    RP*   -| 

              APT*  -| 
              
              TCL** -|

              ICD*  -|

              ECL*  -/
```

The (*) entities may be directly changed by the user. A change in any of them will snowball a full data processing of dependent entities. For example:

* Changing the active Employees spreadsheet will trigger Employees (EE) and Employee Travel History (ETH) processing
* Modifying assumptions (APT) will update Employee Travel History (ETH)
* Adding a Report Period will similarly reprocess ETH

The (**) entities may be changed by admin users.

## Additional Clarifications/User Input

Some of the processing tasks requires the user to provide more information, for example to confirm an Employee home country. Such information should
be stored in a way that amending traveller data/employees spreadsheet does not causes it to be lost, i.e. the client should not be asked to confirm
an employee home country twice for the same exact date period even if the client deletes and uploads the traveller data again.

## Asynchronous Processing

Whenever a user changes a relevant entity, the system will update the `last_travel_history_request` (timestamp) field in the `customers` table.

After that it will delay a celery task responsible for processing the new version. This task will receive the timestamp and customer id as parameters.

The celery task will first collect all the data it needs to process the employee travel history. Then it will process the data. After that it will store
the employee travel history and erase all stale versions, in order to keep the database clean.
