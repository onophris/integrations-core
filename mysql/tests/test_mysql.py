# (C) Datadog, Inc. 2010-2017
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

import pytest
import logging
import copy

from os import environ

from datadog_checks.mysql import MySql
from datadog_checks.utils.platform import Platform

import common
import variables
import tags
import common_config

log = logging.getLogger('test_mysql')


def test_minimal_config(aggregator, spin_up_mysql):
    mysql_check = MySql(common.CHECK_NAME, {}, {})
    mysql_check.check(common_config.MYSQL_MINIMAL_CONFIG)

    # Test service check
    aggregator.assert_service_check('mysql.can_connect', status=MySql.OK,
                                    tags=tags.SC_TAGS_MIN, count=1)

    # Test metrics
    testable_metrics = (variables.STATUS_VARS + variables.VARIABLES_VARS + variables.INNODB_VARS +
                        variables.BINLOG_VARS + variables.SYSTEM_METRICS + variables.SYNTHETIC_VARS)

    for mname in testable_metrics:
        aggregator.assert_metric(mname, at_least=0)


def test_complex_config(aggregator, spin_up_mysql):
    mysql_check = MySql(common.CHECK_NAME, {}, {}, instances=[common_config.MYSQL_COMPLEX_CONFIG])
    mysql_check.check(common_config.MYSQL_COMPLEX_CONFIG)

    # Test service check
    aggregator.assert_service_check('mysql.can_connect', status=MySql.OK,
                                    tags=tags.SC_TAGS, count=1)

    aggregator.assert_service_check('mysql.replication.slave_running', status=MySql.OK,
                                    tags=tags.SC_TAGS, at_least=1)

    ver = map(lambda x: int(x), mysql_check.mysql_version[mysql_check._get_host_key()])
    ver = tuple(ver)

    testable_metrics = (variables.STATUS_VARS + variables.VARIABLES_VARS +
                        variables.INNODB_VARS + variables.BINLOG_VARS +
                        variables.SYSTEM_METRICS + variables.SCHEMA_VARS +
                        variables.SYNTHETIC_VARS)

    if ver >= (5, 6, 0) and environ.get('MYSQL_FLAVOR') != 'mariadb':
        testable_metrics.extend(variables.PERFORMANCE_VARS)

    # Test metrics
    for mname in testable_metrics:
        # These two are currently not guaranteed outside of a Linux
        # environment.
        if mname == 'mysql.performance.user_time' and not Platform.is_linux():
            continue
        if mname == 'mysql.performance.kernel_time' and not Platform.is_linux():
            continue
        if mname == 'mysql.performance.cpu_time' and Platform.is_windows():
            continue

        if mname == 'mysql.performance.query_run_time.avg':
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:testdb'],
                                     count=1)
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:mysql'],
                                     count=1)
        elif mname == 'mysql.info.schema.size':
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:testdb'],
                                     count=1)
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:information_schema'],
                                     count=1)
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:performance_schema'],
                                     count=1)
        else:
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS,
                                     at_least=0)

    # TODO: test this if it is implemented
    # Assert service metadata
    # version_metadata = mysql_check.service_metadata['version']
    # assert len(version_metadata) == 1

    # test custom query metrics
    aggregator.assert_metric('alice.age', value=25)
    aggregator.assert_metric('bob.age', value=20)

    # test optional metrics
    optional_metrics = (variables.OPTIONAL_REPLICATION_METRICS +
                        variables.OPTIONAL_INNODB_VARS +
                        variables.OPTIONAL_STATUS_VARS +
                        variables.OPTIONAL_STATUS_VARS_5_6_6)
    _test_optional_metrics(aggregator, optional_metrics, 1)

    # Raises when coverage < 100%
    aggregator.assert_all_metrics_covered()


def test_connection_failure(aggregator, spin_up_mysql):
    """
    Service check reports connection failure
    """
    mysql_check = MySql(common.CHECK_NAME, {}, {}, instances=[common_config.CONNECTION_FAILURE])

    with pytest.raises(Exception):
        mysql_check.check(common_config.CONNECTION_FAILURE)

    aggregator.assert_service_check('mysql.can_connect', status=MySql.CRITICAL,
                                    tags=tags.SC_FAILURE_TAGS, count=1)

    aggregator.assert_all_metrics_covered()


def test_complex_config_replica(aggregator, spin_up_mysql):
    mysql_check = MySql(common.CHECK_NAME, {}, {})
    config = copy.deepcopy(common_config.MYSQL_COMPLEX_CONFIG)
    config['port'] = common.SLAVE_PORT
    mysql_check.check(config)

    # self.assertMetricTag('mysql.replication.seconds_behind_master', 'channel:default')

    # Test service check
    aggregator.assert_service_check('mysql.can_connect', status=MySql.OK,
                                    tags=tags.SC_TAGS_REPLICA, count=1)

    # Travis MySQL not running replication - FIX in flavored test.
    aggregator.assert_service_check('mysql.replication.slave_running', status=MySql.OK,
                                    tags=tags.SC_TAGS_REPLICA, at_least=1)

    ver = map(lambda x: int(x), mysql_check.mysql_version[mysql_check._get_host_key()])
    ver = tuple(ver)

    testable_metrics = (variables.STATUS_VARS + variables.VARIABLES_VARS +
                        variables.INNODB_VARS + variables.BINLOG_VARS +
                        variables.SYSTEM_METRICS + variables.SCHEMA_VARS +
                        variables.SYNTHETIC_VARS)

    # Test metrics
    for mname in testable_metrics:
        # These two are currently not guaranteed outside of a Linux
        # environment.
        if mname == 'mysql.performance.user_time' and not Platform.is_linux():
            continue
        if mname == 'mysql.performance.kernel_time' and not Platform.is_linux():
            continue
        if mname == 'mysql.performance.cpu_time' and Platform.is_windows():
            continue

        if mname == 'mysql.performance.query_run_time.avg':
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:testdb'], count=1)
        elif mname == 'mysql.info.schema.size':
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:testdb'], count=1)
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:information_schema'], count=1)
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS+['schema:performance_schema'], count=1)
        else:
            aggregator.assert_metric(mname,
                                     tags=tags.METRIC_TAGS, at_least=0)

    # test custom query metrics
    aggregator.assert_metric('alice.age', value=25)
    aggregator.assert_metric('bob.age', value=20)

    # test optional metrics
    optional_metrics = (variables.OPTIONAL_REPLICATION_METRICS +
                        variables.OPTIONAL_INNODB_VARS +
                        variables.OPTIONAL_STATUS_VARS +
                        variables.OPTIONAL_STATUS_VARS_5_6_6)
    _test_optional_metrics(aggregator, optional_metrics, 1)

    # Raises when coverage < 100%
    aggregator.assert_all_metrics_covered()


def _test_optional_metrics(aggregator, optional_metrics, at_least):
    """
    Check optional metrics - there should be at least `at_least` matches
    """

    before = len(aggregator.not_asserted())

    for mname in optional_metrics:
        aggregator.assert_metric(mname, tags=tags.METRIC_TAGS, at_least=0)

    # Compute match rate
    after = len(aggregator.not_asserted())

    assert before - after > at_least
