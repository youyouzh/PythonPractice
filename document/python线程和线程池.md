# Python线程和线程池

## 线程模块`threading`

`threading`模块提供了基于线程的并行支持，该模块是在较低级的模块`_thread`基础上建立的较高级的线程接口。官方文档可以参考： <https://docs.python.org/zh-cn/3.7/library/threading.html#>.

如果需要进程级别的同步，则可以选择`multiprocessing`模块。

### `threading`的基本方法

`threading`模块中常用的函数如下：

- `threading.active_count()`: 返回当前存活的线程类 Thread 对象。返回的计数等于 enumerate() 返回的列表长度。
- `threading.current_thread()`: 返回当前对应调用者的控制线程的 Thread 对象。如果调用者的控制线程不是利用 threading 创建，会返回一个功能受限的虚拟线程对象
- `threading.get_ident()`: 返回当前线程的 “线程标识符”，线程标识符可能会在线程退出，新线程创建时被复用。
- `threading.enumerate()`: 以列表形式返回当前所有存活的 Thread 对象，该列表包含守护线程，current_thread() 创建的虚拟线程对象和主线程。它不包含已终结的线程和尚未开始的线程。
- `threading.main_thread()`: 返回主 Thread 对象。一般情况下，主线程是Python解释器开始时创建的线程
- `threading.local()`: 创建一个 local （或者一个子类型）的实例，管理线程本地数据，在不同的线程中，实例的值会不同

### 线程`Thread`对象

通过`threading.Thread()`可以创建一个`Thread`线程对象。其原型如下：

`class threading.Thread(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None)`

调用这个构造函数时，必需带有关键字参数。参数如下：

- `group`: 应该为`None`；为了日后扩展`ThreadGroup`类实现而保留。
- `target`: 是用于`run()`方法调用的可调用对象。默认是`None`，表示不需要调用任何方法。
- `name`: 是线程名称。默认情况下，由 "Thread-N" 格式构成一个唯一的名称，其中`N`是小的十进制数。
- `args`: 是用于调用目标函数的参数元组。默认是`()`。
- `kwargs`: 是用于调用目标函数的关键字参数字典。默认是`{}`。

如果子类型重载了构造函数，它一定要确保在做任何事前，先发起调用基类构造器(`Thread.__init__()`)。

`Thread`对象常用的方法和属性如下：

- `start()`
  - 开始线程活动。
  - 它在一个线程里最多只能被调用一次
  - 它安排对象的 run() 方法在一个独立的控制进程中调用
  - 如果同一个线程对象中调用这个方法的次数大于一次，会抛出`RuntimeError`
- `run()`
  - 代表线程活动的方法
  - 你可以在子类型里重载这个方法
  - 标准的`run()`方法会对作为`target`参数传递给该对象构造器的可调用对象（如果存在）发起调用，并附带从`args`和`kwargs`参数分别获取的位置和关键字参数
- `join(timeout=None)`
  - 等待，直到线程终结
  - 这会阻塞调用这个方法的线程，直到被调用 join() 的线程终结 -- 不管是正常终结还是抛出未处理异常 -- 或者直到发生超时，超时选项是可选的。
  - 当`timeout`参数存在而且不是`None`时，它应该是一个用于指定操作超时的以秒为单位的浮点数（或者分数）。因为`join()`总是返回`None`，所以你一定要在 `join()`后调用`is_alive()`才能判断是否发生超时 -- 如果线程仍然存活，则`join()`超时。
  - 当`timeout`参数不存在或者是`None`，这个操作会阻塞直到线程终结。
  - 一个线程可以被`join()`很多次。
  - 如果尝试加入当前线程会导致死锁，`join()`会引起`RuntimeError`异常。如果尝试`join()`一个尚未开始的线程，也会抛出相同的异常。
- `is_alive()`
  - 返回线程是否存活。
  - 当`run()`方法刚开始直到`run()`方法刚结束，这个方法返回`True`。模块函数`enumerate()`返回包含所有存活线程的列表。
- `name`
  - 只用于识别的字符串。它没有语义。多个线程可以赋予相同的名称。 初始名称由构造函数设置。
- `ident`
  - 这个线程的 '线程标识符'，如果线程尚未开始则为`None`
  - 这是个非零整数
  - 当一个线程退出而另外一个线程被创建，线程标识符会被复用。即使线程退出后，仍可得到标识符
- `daemon`
  - 一个表示这个线程是（`True`）否（`False`）守护线程的布尔值
  - 一定要在调用`start()`前设置好，不然会抛出`RuntimeError`
  - 初始值继承于创建线程；主线程不是守护线程，因此主线程创建的所有线程默认都是`daemon = False`。
  - 当没有存活的非守护线程时，整个Python程序才会退出。

当线程对象一但被创建，其活动一定会因调用线程的`start()`方法开始。这会在独立的控制线程调用`run()`方法。

一旦线程活动开始，该线程会被认为是 '存活的'，当它的 run() 方法终结了（不管是正常的还是抛出未被处理的异常），就不是'存活的'，`is_alive()`方法用于检查线程是否存活。

其他线程可以调用一个线程的`join()`方法。这会阻塞调用该方法的线程，直到被调用`join()`方法的线程终结。

线程有名字。名字可以传递给构造函数，也可以通过`name`属性读取或者修改。

一个线程可以被标记成一个“守护线程”。 这个标志的意义是，当剩下的线程都是守护线程时，整个 Python 程序将会退出。 初始值继承于创建线程。 这个标志可以通过 daemon``特征属性或者`daemon`构造器参数来设置。

### 线程`Thread`的创建和使用

创建线程并运行：

```python
import threading
import time

def run(n):
    print("task", n)
    time.sleep(1)
    print('2s')
    time.sleep(1)
    print('1s')
    time.sleep(1)
    print('0s')
    time.sleep(1)

if __name__ == '__main__':
    t1 = threading.Thread(target=run, args=("t1",))
    t2 = threading.Thread(target=run, args=("t2",))
    t1.start()
    t2.start()

----------------------------------

>>> task t1
>>> task t2
>>> 2s
>>> 2s
>>> 1s
>>> 1s
>>> 0s
>>> 0s
```

可以通过继承`threading.Thread`来自定义线程类，其本质是重构`Thread`类中的`run()`方法。

```python
import threading
import time

class MyThread(threading.Thread):
    def __init__(self, n):
        super(MyThread, self).__init__()  # 重构run函数必须要写
        self.n = n

    def run(self):
        print("task", self.n)
        time.sleep(1)
        print('2s')
        time.sleep(1)
        print('1s')
        time.sleep(1)
        print('0s')
        time.sleep(1)

if __name__ == "__main__":
    t1 = MyThread("t1")
    t2 = MyThread("t2")
    t1.start()
    t2.start()
    
----------------------------------

>>> task t1
>>> task t2
>>> 2s
>>> 2s
>>> 1s
>>> 1s
>>> 0s
>>> 0s
```

当设置线程为守护线程时，如果守护线程结束，则守护线程下的所有子线程也会立即结束。

```python
import threading
import time

def run(n):
    print("task", n)
    time.sleep(1)       #此时子线程停1s
    print('3')
    time.sleep(1)
    print('2')
    time.sleep(1)
    print('1')

if __name__ == '__main__':
    t = threading.Thread(target=run, args=("t1",))
    t.setDaemon(True)   #把子进程设置为守护线程，必须在start()之前设置
    t.start()
    print("end")
    
----------------------------------

>>> task t1
>>> end
```

使用`join()`方法可以让守护线程执行结束之后，主线程再结束，主线程等待子线程执行。

```python
import threading
import time

def run(n):
    print("task", n)
    time.sleep(1)       #此时子线程停1s
    print('3')
    time.sleep(1)
    print('2')
    time.sleep(1)
    print('1')

if __name__ == '__main__':
    t = threading.Thread(target=run, args=("t1",))
    t.setDaemon(True)   #把子进程设置为守护线程，必须在start()之前设置
    t.start()
    t.join() # 设置主线程等待子线程结束
    print("end")

----------------------------------

>>> task t1
>>> 3
>>> 2
>>> 1
>>> end
```

## 线程池及其原理和使用

系统启动一个新线程的成本是比较高的，因为它涉及与操作系统的交互。在这种情形下，使用线程池可以很好地提升性能，尤其是当程序中需要创建大量生存期很短暂的线程时，更应该考虑使用线程池。

线程池在系统启动时即创建大量空闲的线程，程序只要将一个函数提交给线程池，线程池就会启动一个空闲的线程来执行它。当该函数执行结束后，该线程并不会死亡，而是再次返回到线程池中变成空闲状态，等待执行下一个函数。

此外，使用线程池可以有效地控制系统中并发线程的数量。当系统中包含有大量的并发线程时，会导致系统性能急剧下降，甚至导致 Python 解释器崩溃，而线程池的最大线程数参数可以控制系统中并发线程的数量不超过此数。

### 线程池的使用

线程池的基类是`concurrent.futures`模块中的`Executor`，`Executor`提供了两个子类，即`ThreadPoolExecutor`和`ProcessPoolExecutor`，其中`ThreadPoolExecutor`用于创建线程池，而`ProcessPoolExecutor`用于创建进程池。

如果使用线程池/进程池来管理并发编程，那么只要将相应的`task`函数提交给线程池/进程池，剩下的事情就由线程池/进程池来搞定。

Exectuor 提供了如下常用方法：

- `submit(fn, *args, **kwargs)`：将`fn`函数提交给线程池。`*args`代表传给`fn`函数的参数，`*kwargs`代表以关键字参数的形式为`fn`函数传入参数。
- `map(func, *iterables, timeout=None, chunksize=1)`：该函数类似于全局函数`map(func, *iterables)`，只是该函数将会启动多个线程，以异步方式立即对 `iterables`执行`map`处理。
- `shutdown(wait=True)`：关闭线程池。

程序将`task`函数提交（submit）给线程池后，`submit`方法会返回一个`Future`对象，`Future`类主要用于获取线程任务函数的返回值。由于线程任务会在新线程中以异步方式执行，因此，线程执行的函数相当于一个“将来完成”的任务，所以 Python 使用`Future`来代表。

`Future`提供了如下方法：

- `cancel()`：取消该`Future`代表的线程任务。如果该任务正在执行，不可取消，则该方法返回`False`；否则，程序会取消该任务，并返回`True`。
- `cancelled()`：返回`Future`代表的线程任务是否被成功取消。
- `running()`：如果该`Future`代表的线程任务正在执行、不可被取消，该方法返回`True`。
- `done()`：如果该`Future`代表的线程任务被成功取消或执行完成，则该方法返回`True`。
- `result(timeout=None)`：获取该`Future`代表的线程任务最后返回的结果。如果`Future`代表的线程任务还未完成，该方法将会阻塞当前线程，其中`timeout`参数指定最多阻塞多少秒。
- `exception(timeout=None)`：获取该`Future`代表的线程任务所引发的异常。如果该任务成功完成，没有异常，则该方法返回`None`。
- `add_done_callback(fn)`：为该`Future`代表的线程任务注册一个“回调函数”，当该任务成功完成时，程序会自动触发该 fn 函数。

在用完一个线程池后，应该调用该线程池的`shutdown()`方法，该方法将启动线程池的关闭序列。调用`shutdown()`方法后的线程池不再接收新任务，但会将以前所有的已提交任务执行完成。当线程池中的所有任务都执行完成后，该线程池中的所有线程都会死亡。

使用线程池来执行线程任务的步骤如下：

1. 调用`ThreadPoolExecutor`类的构造器创建一个线程池。
2. 定义一个普通函数作为线程任务。
3. 调用`ThreadPoolExecutor`对象的`submit()`方法来提交线程任务。
4. 当不想提交任何任务时，调用`ThreadPoolExecutor`对象的`shutdown()`方法来关闭线程池。

下面程序示范了如何使用线程池来执行线程任务：

```python
from concurrent.futures import ThreadPoolExecutor
import threading
import time
# 定义一个准备作为线程任务的函数
def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum
# 创建一个包含2条线程的线程池
pool = ThreadPoolExecutor(max_workers=2)
# 向线程池提交一个task, 50会作为action()函数的参数
future1 = pool.submit(action, 50)
# 向线程池再提交一个task, 100会作为action()函数的参数
future2 = pool.submit(action, 100)
# 判断future1代表的任务是否结束
print(future1.done())
time.sleep(3)
# 判断future2代表的任务是否结束
print(future2.done())
# 查看future1代表的任务返回的结果
print(future1.result())
# 查看future2代表的任务返回的结果
print(future2.result())
# 关闭线程池
pool.shutdown()
```

上面程序中，第 13 行代码创建了一个包含两个线程的线程池，接下来的两行代码只要将`action()`函数提交`（submit）`给线程池，该线程池就会负责启动线程来执行 `action()`函数。这种启动线程的方法既优雅，又具有更高的效率。

当程序把`action()`函数提交给线程池时，`submit()`方法会返回该任务所对应的`Future`对象，程序立即判断 futurel 的`done()`方法，该方法将会返回`False`（表明此时该任务还未完成）。接下来主程序暂停 3 秒，然后判断 future2 的 done() 方法，如果此时该任务已经完成，那么该方法将会返回`True`。

程序最后通过`Future`的`result()`方法来获取两个异步任务返回的结果。

当程序使用`Future`的`result()`方法来获取结果时，该方法会阻塞当前线程，如果没有指定`timeout`参数，当前线程将一直处于阻塞状态，直到`Future`代表的任务返回。

### 获取执行结果

前面程序调用了`Future`的`result()`方法来获取线程任务的运回值，但该方法会阻塞当前主线程，只有等到钱程任务完成后，`result()`方法的阻塞才会被解除。

如果程序不希望直接调用`result()`方法阻塞线程，则可通过`Future`的`add_done_callback()`方法来添加回调函数，该回调函数形如`fn(future)`。当线程任务完成后，程序会自动触发该回调函数，并将对应的`Future`对象作为参数传给该回调函数。

下面程序使用`add_done_callback()`方法来获取线程任务的返回值：

```python
from concurrent.futures import ThreadPoolExecutor
import threading
import time
# 定义一个准备作为线程任务的函数
def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum
# 创建一个包含2条线程的线程池
with ThreadPoolExecutor(max_workers=2) as pool:
    # 向线程池提交一个task, 50会作为action()函数的参数
    future1 = pool.submit(action, 50)
    # 向线程池再提交一个task, 100会作为action()函数的参数
    future2 = pool.submit(action, 100)
    def get_result(future):
        print(future.result())
    # 为future1添加线程完成的回调函数
    future1.add_done_callback(get_result)
    # 为future2添加线程完成的回调函数
    future2.add_done_callback(get_result)
    print('--------------')
```

上面主程序分别为 future1、future2 添加了同一个回调函数，该回调函数会在线程任务结束时获取其返回值。

主程序的最后一行代码打印了一条横线。由于程序并未直接调用 future1、future2 的`result()`方法，因此主线程不会被阻塞，可以立即看到输出主线程打印出的横线。接下来将会看到两个新线程并发执行，当线程任务执行完成后，`get_result()`函数被触发，输出线程任务的返回值。

另外，由于线程池实现了上下文管理协议（Context Manage Protocol），因此，程序可以使用 with 语句来管理线程池，这样即可避免手动关闭线程池，如上面的程序所示。

此外，`Exectuor`还提供了一个`map(func, *iterables, timeout=None, chunksize=1)`方法，该方法的功能类似于全局函数`map()`，区别在于线程池的`map()`方法会为`iterables`的每个元素启动一个线程，以并发方式来执行`func`函数。这种方式相当于启动`len(iterables)`个线程，井收集每个线程的执行结果。

例如，如下程序使用`Executor`的`map()`方法来启动线程，并收集线程任务的返回值：

```python
from concurrent.futures import ThreadPoolExecutor
import threading
import time
# 定义一个准备作为线程任务的函数
def action(max):
    my_sum = 0
    for i in range(max):
        print(threading.current_thread().name + '  ' + str(i))
        my_sum += i
    return my_sum
# 创建一个包含4条线程的线程池
with ThreadPoolExecutor(max_workers=4) as pool:
    # 使用线程执行map计算
    # 后面元组有3个元素，因此程序启动3条线程来执行action函数
    results = pool.map(action, (50, 100, 150))
    print('--------------')
    for r in results:
        print(r)
```

上面程序使用`map()`方法来启动 3 个线程（该程序的线程池包含 4 个线程，如果继续使用只包含两个线程的线程池，此时将有一个任务处于等待状态，必须等其中一个任务完成，线程空闲出来才会获得执行的机会），`map()`方法的返回值将会收集每个线程任务的返回结果。

运行上面程序，同样可以看到 3 个线程并发执行的结果，最后通过 results 可以看到 3 个线程任务的返回结果。

通过上面程序可以看出，使用`map()`方法来启动线程，并收集线程的执行结果，不仅具有代码简单的优点，而且虽然程序会以并发方式来执行`action()`函数，但最后收集的`action()`函数的执行结果，依然与传入参数的结果保持一致。也就是说，上面 results 的第一个元素是`action(50)`的结果，第二个元素是`action(100)`的结果，第三个元素是`action(150)`的结果。

## 线程池`threadpool`模块

线程池`threadpool`的简单使用方法：

```python
import time
import threadpool

def sayhello(str):
    print("Hello ", str)
    time.sleep(2)

name_list =['a','b','c','d']
start_time = time.time()
pool = threadpool.ThreadPool(10) 
requests = threadpool.makeRequests(sayhello, name_list) 
[pool.putRequest(req) for req in requests] 
pool.wait() 
print('%d second'% (time.time()-start_time))
```

创建和使用线程池的步骤如下：

1. 使用`threadpool.ThreadPool(10)`定义一个大小为10的线程池
2. 调用`threadpool.makeRequests`创建了要开启多线程的函数，以及函数相关参数和回调函数
3. 将所有要运行多线程的请求放入线程池
4. 等待所有的线程完成工作后退出

注意到其中的`threadpool.makeRequests`，两个参数即可运行，第三个参数可以配置一个回调函数。当运行的函数有多个参数时，使用下面的方式：

```python
import threadpool

def hello(m, n, o):
    print("m = %s, n = %s, o = %s"%(m, n, o))
     
 
if __name__ == '__main__':
    # 方法1  
    lst_vars_1 = ['1', '2', '3']
    lst_vars_2 = ['4', '5', '6']
    func_var = [(lst_vars_1, None), (lst_vars_2, None)]
    
    # 方法2
    dict_vars_1 = {'m':'1', 'n':'2', 'o':'3'}
    dict_vars_2 = {'m':'4', 'n':'5', 'o':'6'}
    func_var = [(None, dict_vars_1), (None, dict_vars_2)]    
     
    pool = threadpool.ThreadPool(2)
    requests = threadpool.makeRequests(hello, func_var)
    [pool.putRequest(req) for req in requests]
    pool.wait()
```
