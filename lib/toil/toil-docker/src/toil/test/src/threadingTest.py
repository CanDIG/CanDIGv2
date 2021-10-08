import logging
import multiprocessing
import os
import random
import time
import traceback
from functools import partial

from toil.lib.threading import LastProcessStandingArena, global_mutex
from toil.test import ToilTest, travis_test

log = logging.getLogger(__name__)

class ThreadingTest(ToilTest):
    """
    Test Toil threading/synchronization tools
    """

    @travis_test
    def testGlobalMutexOrdering(self):
        for it in range(10):
            log.info('Iteration %d', it)

            scope = self._createTempDir()
            mutex = 'mutex'
            # Use processes (as opposed to threads) to prevent GIL from ordering things artificially
            pool = multiprocessing.Pool()
            try:
                numTasks = 100
                results = pool.map_async(
                    func=partial(_testGlobalMutexOrderingTask, scope, mutex),
                    iterable=list(range(numTasks)))
                results = results.get()
            finally:
                pool.close()
                pool.join()

            self.assertEqual(len(results), numTasks)
            for item in results:
                # Make sure all workers say they succeeded
                self.assertEqual(item, True)

    @travis_test
    def testLastProcessStanding(self):
        for it in range(10):
            log.info('Iteration %d', it)

            scope = self._createTempDir()
            arena_name = 'thunderdome'
            # Use processes (as opposed to threads) to prevent GIL from ordering things artificially
            pool = multiprocessing.Pool()
            try:
                numTasks = 100
                results = pool.map_async(
                    func=partial(_testLastProcessStandingTask, scope, arena_name),
                    iterable=list(range(numTasks)))
                results = results.get()
            finally:
                pool.close()
                pool.join()

            self.assertEqual(len(results), numTasks)
            for item in results:
                # Make sure all workers say they succeeded
                self.assertEqual(item, True)
            for filename in os.listdir(scope):
                assert not filename.startswith('precious'), "File {} still exists".format(filename)

def _testGlobalMutexOrderingTask(scope, mutex, number):
    try:
        # We will all fight over the potato
        potato = os.path.join(scope, 'potato')

        with global_mutex(scope, mutex):
            log.info('PID %d = num %d running', os.getpid(), number)
            assert not os.path.exists(potato), "We see someone else holding the potato file"

            # Put our name there
            with open(potato, 'w') as out_stream:
                out_stream.write(str(number))

            # Wait
            time.sleep(random.random() * 0.01)

            # Make sure our name is still there
            with open(potato, 'r') as in_stream:
                seen = in_stream.read().rstrip()
                assert seen == str(number), "We are {} but {} stole our potato!".format(number, seen)

            os.unlink(potato)
            assert not os.path.exists(potato), "We left the potato behind"
            log.info('PID %d = num %d dropped potato', os.getpid(), number)
        return True
    except:
        traceback.print_exc()
        return False

def _testLastProcessStandingTask(scope, arena_name, number):
    try:
        arena = LastProcessStandingArena(scope, arena_name)

        arena.enter()
        log.info('PID %d = num %d entered arena', os.getpid(), number)
        try:
            # We all make files
            my_precious = os.path.join(scope, 'precious' + str(number))

            # Put our name there
            with open(my_precious, 'w') as out_stream:
                out_stream.write(str(number))

            # Wait
            time.sleep(random.random() * 0.01)

            # Make sure our file is still there unmodified
            assert os.path.exists(my_precious), "Precious file {} has been stolen!".format(my_precious)
            with open(my_precious, 'r') as in_stream:
                seen = in_stream.read().rstrip()
                assert seen == str(number), "We are {} but saw {} in our precious file!".format(number, seen)
        finally:
            was_last = False
            for _ in arena.leave():
                was_last = True
                log.info('PID %d = num %d is last standing', os.getpid(), number)

                # Clean up all the files
                for filename in os.listdir(scope):
                    if filename.startswith('precious'):
                        log.info('PID %d = num %d cleaning up %s', os.getpid(), number, filename)
                        os.unlink(os.path.join(scope, filename))

            log.info('PID %d = num %d left arena', os.getpid(), number)

        return True
    except:
        traceback.print_exc()
        return False
