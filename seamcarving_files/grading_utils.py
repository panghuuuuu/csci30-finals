#!/usr/bin/env python3

from subprocess import Popen
import unittest
import sys
import time

# is this gonna run in codepost?
CODEPOST = False

def report_result(category, case, res, logs=''):
    detail = logs
    reporter = f'TestOutput "{category}" "{case}" {"true" if res else "false"} "{detail}"'
    if CODEPOST:
        # Popen(['/bin/bash', '-c', reporter])
        print('[DEBUG]', reporter)
    else:
        pass

class score:
    '''
    Score decorator
    '''
    def __init__(self, val):
        self.val = val

    def __call__(self, func):
        func.__score__ = self.val
        return func

class BruhTestResult(unittest.TestResult):
    def __init__(self, stream, descriptions, verbosity, results, category):
        super(BruhTestResult, self).__init__(stream, descriptions, verbosity)
        self.descriptions = descriptions
        self.results = results
        self.category = category

    def get_description(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return doc_first_line
        else:
            return str(test)

    def get_score(self, test):
        return getattr(getattr(test, test._testMethodName), '__score__', None)

    def startTest(self, test):
        super(BruhTestResult, self).startTest(test)

    def get_output(self):
        if self.buffer:
            out = self._stdout_buffer.getvalue()
            err = self._stderr_buffer.getvalue()
            if err:
                if not out.endswith('\n'):
                    out += '\n'
                out += err
            return out

    def build_result(self, test, err=None):
        failed = err is not None
        score = self.get_score(test)
        output = self.get_output() or ''
        category = self.category or 'default'
        test_id = str(test)

        result = {'name': self.get_description(test)}
        result['passed'] = not failed
        result['category'] = category
        result['id'] = test_id
        if score is not None:
            result['score'] = 0 if failed else score
            result['max_score'] = score
            # also mark failed if points are lost
            failed |= result['score'] < score
        #if output:
        result['output'] = output
        if err:
            result['errors'] = f'{str(err[0].__name__)}: {str(err[1])}\n'
        else:
            result['errors'] = ''
        return result


    def process_result(self, test, err=None):
        self.results.append(self.build_result(test, err))

    def addFailure(self, test, err):
        super(BruhTestResult, self).addFailure(test, err)
        self.process_result(test, err)

    def addError(self, test, err):
        super(BruhTestResult, self).addError(test, err)
        self.process_result(test, err)

    def addSuccess(self, test):
        super(BruhTestResult, self).addSuccess(test)
        self.process_result(test)


class BruhTestRunner:
    resultclass = BruhTestResult

    def __init__(self, stream=sys.stdout, descriptions=True, verbosity=1, failfast=False, buffer=True, category='default'):
        self.stream = stream
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.category = category
        #self.tb_locals = False
        self.results = []

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity, self.results, self.category)

    def run(self, test):
        result = self._makeResult()
        result.failfast = self.failfast
        #result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime

        #self.json_data["execution_time"] = format(timeTaken, "0.2f")
        total_score = 0
        max_score = 0
        for ts in self.results:
            #print(ts)
            if ts['passed']:
                # icon = color('✔', fg='green')
                # icon = '✔'
                icon = 'PASS'
            else:
                # icon = color('✘', fg='red')
                # icon = '✘'
                icon = 'FAIL'
            name = ts['name']
            total_score += ts.get('score', 0)
            max_score += ts.get('max_score', 0)

            #self.stream.write(color(f'{icon} {name}\n', fg=('green' if ts['passed'] else 'red')))
            output = f'{icon} [{ts["score"]}] {name}'
            if ts['errors']:
                for line in ts['errors'].split('\n'):
                    output += f'\n     {line}'
            if CODEPOST:
                report_result(self.category, ts['id'], ts['passed'], ts['output'] + ts['errors'] + f'{output}\n')
            else:
                self.stream.write(f'{output}\n')

        if not CODEPOST:
            self.stream.write('\n')
            self.stream.write(f'Total score: {total_score}/{max_score}\n')
        return result
