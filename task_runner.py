import unittest
import threading, heapq
from time import sleep

class ThreadPool:
    def __init__(self, numThreads):
        self.__threads = []
        self.__resizeLock = threading.Lock()
        self.__taskLock = threading.Lock()
        self.__startEvent = threading.Event()
        self.__tasks = []
        self.__isJoining = False
        self.setThreadCount(int(numThreads))
    
    def start(self):
        self.__startEvent.set()
        
    def pause(self):
        self.__startEvent.clear()
        
    def wait_running(self, timeout):
        self.__startEvent.wait(timeout)
        return self.__startEvent.is_set()

    def setThreadCount(self, newNumThreads):
        # Can't change the thread count if we're shutting down the pool!
        if self.__isJoining:
            return False
        self.__resizeLock.acquire()
        try:
            self.__setThreadCountNolock(newNumThreads)
        finally:
            self.__resizeLock.release()
        return True

    def __setThreadCountNolock(self, newNumThreads):
        # If we need to grow the pool, do so
        while newNumThreads > len(self.__threads):
            newThread = ThreadPoolThread(self)
            self.__threads.append(newThread)
            newThread.start()
        # If we need to shrink the pool, do so
        while newNumThreads < len(self.__threads):
            self.__threads[0].goAway()
            del self.__threads[0]

    def getThreadCount(self):
        self.__resizeLock.acquire()
        try:
            return len(self.__threads)
        finally:
            self.__resizeLock.release()

    def queueTask(self, task, args=None, taskCallback=None, priority=0):
        if self.__isJoining == True:
            return False
        if not callable(task):
            return False
        self.__taskLock.acquire()
        try:

            heapq.heappush(self.__tasks, (priority, (task, args, taskCallback)))
            return True
        finally:
            self.__taskLock.release()

    def getNextTask(self):
        self.__taskLock.acquire()
        try:
            if self.__tasks == []:
                return (None, None, None)
            else:
                return heapq.heappop(self.__tasks)[1]
        finally:
            self.__taskLock.release()

    def joinAll(self, waitForTasks=True, waitForThreads=True):
        # Mark the pool as joining to prevent any more task queueing
        self.__isJoining = True
        # Wait for tasks to finish
        if waitForTasks:
            while self.__tasks != []:
                sleep(.1)
        # Tell all the threads to quit
        self.__resizeLock.acquire()
        try:
            self.__setThreadCountNolock(0)
            self.__isJoining = True
            # Wait until all threads have exited
            if waitForThreads:
                for t in self.__threads:
                    t.join()
                    del t
            # Reset the pool for potential reuse
            self.__isJoining = False
        finally:
            self.__resizeLock.release()

class ThreadPoolThread(threading.Thread):
    name = "ThreadPoolThread"
    threadSleepTime = 0.1

    def __init__(self, pool):
        threading.Thread.__init__(self)
        self.__pool = pool
        self.__isDying = False

    def run(self):
        while self.__isDying == False:
            if self.__pool.wait_running(1) == False:
                continue
            cmd, args, callback = self.__pool.getNextTask()
            # If there's nothing to do, just sleep a bit
            if cmd is None:
                sleep(ThreadPoolThread.threadSleepTime)
            elif callback is None:
                cmd(args)
            else:
                callback(cmd(args))

    def goAway(self):
        self.__isDying = True


class Task(object):
    def __init__(self, obj):
        self._argv = obj
        self._result = None

    def run(self, obj):
        raise NotImplemented

    def _set_result(self, result):
        self._result = result

    def get_result(self):
        return self._result

class SyncTask(Task):
    def __init__(self, obj):
        self._argv = obj
        self._wait_for_finish = threading.Event()
        self._result = None
            
    def _set_result(self, result):
        self._result = result
        self._wait_for_finish.set()

    def get_result(self):
        self._wait_for_finish.wait()
        return self._result

class TaskRunner(object):
    def __init__(self, concurrent_number):
        self.__threadpool = ThreadPool(concurrent_number)

    def add_task(self, task_obj, priority=0):
        _argv = None
        _set_result = None
        if hasattr(task_obj, "_argv"):
            _argv = task_obj._argv
        if hasattr(task_obj, "_set_result"):
            _set_result = task_obj._set_result
        self.__threadpool.queueTask(task_obj.run, _argv, _set_result, priority)

    def start(self):
        self.__threadpool.start()
    
    def pause(self):
        self.__threadpool.pause()

    def stop(self):
        self.__threadpool.joinAll(waitForTasks=False, waitForThreads=False)
        
    def join(self):
        self.__threadpool.joinAll(waitForTasks=True, waitForThreads=True)
# test case


class TestTask(Task):
    def run(self, obj):
        sleep(1)
        print obj
        return "OK"
    
class TestSyncTask(SyncTask):
    def run(self, obj):
        sleep(1)
        return "OK"    

class TestTaskRunner(unittest.TestCase):
    def test(self):
        task_runner = TaskRunner(20)
        t = TestTask("4")
        task_runner.add_task(t, 1)
        t.get_result()
        task_runner.add_task(TestTask("3"), 2)
        task_runner.add_task(TestTask("2"), 5)
        task_runner.add_task(TestTask("1"), 5)
        task_runner.add_task(TestTask("4"), 1)
        task_runner.add_task(TestTask("P"))
        task_runner.add_task(TestTask("P"))
        task_runner.add_task(TestTask("P"))
        task_runner.add_task(TestTask("4"), 1)
        task_runner.add_task(TestTask("3"), 2)
        task_runner.add_task(TestTask("P"))
        task_runner.add_task(TestTask("P"))
        task_runner.stop()
        sleep(3)
        
def test():
    task_runner = TaskRunner(20)
    t = TestTask("4")
    task_runner.add_task(t, 1)
    t.get_result()
    task_runner.add_task(TestTask("3"), 2)
    task_runner.add_task(TestTask("2"), 5)
    task_runner.add_task(TestTask("1"), 5)
    task_runner.add_task(TestTask("4"), 1)
    task_runner.add_task(TestTask("P"))
    task_runner.add_task(TestTask("P"))
    task_runner.add_task(TestTask("P"))
    task_runner.add_task(TestTask("4"), 1)
    task_runner.add_task(TestTask("3"), 2)
    task_runner.add_task(TestTask("P"))
    task_runner.add_task(TestTask("P"))
    task_runner.start()
    task_runner.stop()
    sleep(3)
        
if __name__ == '__main__':
    test()
