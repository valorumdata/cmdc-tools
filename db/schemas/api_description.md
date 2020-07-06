# COVID Modeling Data Collaborative API

This page provides documentation for the data availble in the COVID Modeling Data Collaborative's database. It contains:

1. A description of the different datasets, the variables in those datasets, and where those datasets were sourced from
2. An interactive description of the API which describes the fields and allows you to submit sample requests

It is useful to note that the data is mostly stored in _long form_ rather than _wide form_. In long form each data observation, or value, is associated with its unique identifiers. For example, in many of our datasets the identifiers are `dt` (date of the observation), `location` (geography of the observation), and `variable` (name of the variable being observed), and the value of the observation is stored in `value`. This can be seen in the [table in the example subsection](##Examples).


## Query Parameters

There are a two types of parameters that can be included in the queries:

* _Data parameters_: Data parameters are used to select subsets of the data by performing some type of comparison between the parameter argument and the data.
* _Keyword parameters_: Keyword parameters interact with how the data is returned. For example, `select` can modify which columns are returned, `order` changes how the data is ordered when it is returned, and `limit` changes the number of observations returned.

We provide some examples of how you might use these below, but more information can be found at [TODO: this link]().


## Examples

We will do some examples using the example table below:

| ---------- | -------- | -------------------- | ------ |
| dt         | location | variable             | value  |
| ---------- | ----     | -------------------- | ------ |
| 2020-06-01 | 6        | deaths_total         | 4251   |
| 2020-06-01 | 12       | deaths_total         | 2543   |
| 2020-06-01 | 48       | deaths_total         | 1678   |
| 2020-06-02 | 6        | deaths_total         | 4286   |
| 2020-06-02 | 12       | deaths_total         | 2613   |
| 2020-06-02 | 48       | deaths_total         | 1698   |
| 2020-06-01 | 6        | positive_tests_total | 113006 |
| 2020-06-01 | 12       | positive_tests_total | 56830  |
| 2020-06-01 | 48       | positive_tests_total | 64880  |
| 2020-06-02 | 6        | positive_tests_total | 115310 |
| 2020-06-02 | 12       | positive_tests_total | 57447  |
| 2020-06-02 | 48       | positive_tests_total | 66568  |

If you have further questions, please reach out via github or our website


### Only data from CA

In order to select data from only California (fips code 06) we would use the parameter

* `location=eq.06`


### Only observations with more than 100,000 tests

In order to only select observations with more than 100,000 tests, we would want to use the following parameters

* `variable=eq.positive_tests_total`
* `value=gt.100000`


### Only observations after June 1, 2020

In order to only select the data from after June 1, 2020, we would use the following parameter

* `dt=gt."2020-06-01"`


### Select total deaths for Texas ordered by date

In order to select only the total deaths variable for Texas and have the results be ordered by date, we would use the following parameters

* `location=eq.48`
* `variable=eq.positive_tests_total`
* `order=dt`


## Software

We use the following open source technologies for this API.

* The data is hosted in a [PostgreSQL database](https://www.postgresql.org/)
* The API is built using [PostgREST](http://postgrest.org/en/v7.0.0/)
* The documentation is generated using [Swagger](https://swagger.io/docs/).

We are grateful to all of these projects for simplifying the task of building, deploying, and documenting our API. We are also grateful to Google Cloud for helping us host and distribute our data.
