#coding=utf-8 #Python默认是以ASCII作为编码方式的,不加这句没法显示中文
'''
进程：
具有一定独立功能的程序关于某个数据集合上的一次运行活动，是操作系统进行资源分配和调度的一个独立单位。它可以申请和拥有系统资源，是一个动态的概念，是一个活动的实体。它不只是程序的代码，还包括当前的活动，
通过程序计数器的值和处理寄存器的内容来表示。进程是一个“执行中的程序”。程序是一个没有生命的实体，只有处理器赋予程序生命时，它才能成为一个活动的实体，我们称其为进程。

线程：
线程的一个实体，是CPU调度和分派的基本单位，是比进程更小的能独立运行的基本单位，基本上不用有系统资源，只拥有一点在运行中必不可少的资源
(如程序计数器,一组寄存器和栈)，可与同属一个进程的其他的线程共享进程所拥有的全部资源。由于线程比进程更小，故对它的调度所付出的开销就会小得多，能更高效的提高系统内多个程序间并发执行的程度。

关系：
通常在一个进程中可以包含若干个线程，它们可以利用进程所拥有的资源。在引入线程的操作系统中，通常都是把进程作为分配资源的基本单位，而把线程作为独立运行和独立调度的基本单位。
一个线程可以创建和撤销另一个线程;同一个进程中的多个线程之间可以并发执行。
相对进程而言，线程是一个更加接近于执行体的概念，它可以与同进程中的其他线程共享数据，但拥有自己的栈空间，拥有独立的执行序列。

进程和线程的区别：
a.地址空间和其它资源：进程间相互独立，同一进程的各线程间共享。某进程内的线程在其它进程不可见。
b.通信：进程间通信IPC，线程间可以直接读写进程数据段（如全局变量）来进行通信——需要进程同步和互斥手段的辅助，以保证数据的一致性。
c.调度和切换：线程上下文切换比进程上下文切换要快得多。
d.在多线程OS中，进程不是一个可执行的实体。

进程和线程的主要差别在于它们是不同的操作系统资源管理方式。进程有独立的地址空间，一个进程崩溃后，在保护模式下不会对其它进程产生影响，而线程只是一个进程中的不同执行路径。
线程有自己的堆栈和局部变量，但线程之间没有单独的地址空间，一个线程死掉就等于整个进程死掉，所以多进程的程序要比多线程的程序健壮，但在进程切换时，耗费资源较大，效率要差一些。
但对于一些要求同时进行并且又要共享某些变量的并发操作，只能用线程，不能用进程。

1) 简而言之,一个程序至少有一个进程,一个进程至少有一个线程.

2) 线程的划分尺度小于进程，使得多线程程序的并发性高。

3) 另外，进程在执行过程中拥有独立的内存单元，而多个线程共享内存，从而极大地提高了程序的运行效率。

4) 线程在执行过程中与进程还是有区别的。每个独立的线程有一个程序运行的入口、顺序执行序列和程序的出口。但是线程不能够独立执行，必须依存在应用程序中，由应用程序提供多个线程执行控制。

5) 从逻辑角度来看，多线程的意义在于一个应用程序中，有多个执行部分可以同时执行。但操作系统并没有将多个线程看做多个独立的应用，来实现进程的调度和管理以及资源分配。这就是进程和线程的重要区别。

优缺点
线程和进程在使用上各有优缺点：线程执行开销小，但不利于资源的管理和保护；而进程正相反。同时，线程适合于在SMP机器上运行，而进程则可以跨机器迁移。

如果要启动大量的子进程，可以用进程池的方式批量创建子进程

保证进程安全、同步的方法:
一般说来，线程的安全性主要来源于其运行的并发性和对资源的共享性；进程的安全性主要在应用级别，在于其对系统的威胁性
一般针对已有的进程进行安全方面的控制。如：
在系统安全中发现并清除病毒进程；
在网络应用中，优化守护进程或端口扫描进程；等等
从开发者（编程）的角度，进程的安全所需要考虑的问题和线程类似，但由于线程能够共享进程的资源，所以线程安全一般考虑的问题比进程安全多
方法有：
加上共享资源同步锁
主动阻塞，主动唤醒
对于死锁造成的安全问题：
可以撤消陷于死锁的全部线程。
可以逐个撤消陷于死锁的进程，直到死锁不存在。
从陷于死锁的线程中逐个强迫放弃所占用的资源，直至死锁消失。
对线程生命周期控制如
stop()：停止线程；
suspend()：暂停线程的运行；
resume()：继续线程的运行：
destroy()：让线程销毁；等等。
等类似的来控制进程安全
'''

'''
多线程解决 两个生产者，一个消费者问题
Condition被称为条件变量，除了提供与Lock类似的acquire和release方法外，还提供了wait和notify方法。
使用Condition的主要方式为：
线程首先acquire一个条件变量，然后判断一些条件。如果条件不满足则wait；如果条件满足，进行一些 处理改变条件后，
通过notify方法通知其他线程，其他处于wait状态的线程接到通知后会重新判断条件。不断的重复这一过程，从而解决复杂的同步问 题。
运行环境:python2.7.12
操作系统:windows7 64bit
问题描述：一个生产者每秒钟生产1个产品放入产品池；一个生产者每秒钟生产2个产品放入产品池；一个消费者每秒钟从产品池中消费1-5之间的一个随机数个产品；
         产品池满时，生产者等待，产品池有空位时，生产者继续生产；产品池空时，消费者等待，产品池有产品时，消费者继续消费。每个产品有自己独特的标记。
#设置产品池大小为10
'''
import threading
import time
import random

condition = threading.Condition()
products = 0 #由于是多线程，可以共享同一个变量，所以利用全局变量来进行通信

class Producer(threading.Thread):
    #生产者
    ix = [0]  # 生产者实例个数  闭包，必须是数组，不能直接 ix = 0
    def __init__(self, ix=0):
        super(Producer,self).__init__()
        self.ix[0] += 1
        self.setName('生产者' + str(self.ix[0]))

    def run(self):
        global condition, products
        while True:
            if condition.acquire():
                if products < 10:
                    if self.getName()== '生产者1':
                        products += 1
                        pro=1
                    else:
                        if products<9:
                            products += 2
                            pro=2
                        else:
                            pro=0
                    print("{}：库存不足。生产了%d件产品，现在产品总数量 {}".format(self.getName(), products)%pro)
                    condition.notify()
                else: #产品池满了
                    print("{}：库存充足(10)。现在产品总数量 {}".format(self.getName(), products))
                    condition.wait();
                condition.release()
                time.sleep(1)

class Consumer(threading.Thread):
    #消费者
    ix = [0]  # 消费者实例个数# 闭包，必须是数组，不能直接 ix = 0
    def __init__(self):
        super(Consumer,self).__init__()
        self.ix[0] += 1
        self.setName('消费者' + str(self.ix[0]))
    def run(self):
        global condition, products
        while True:
            if condition.acquire():
                if products >= 1:
                    tmp = random.randint(1, 5)
                    oldproducts =  products
                    products -= tmp
                    if products > 0:
                        print("{}：消费了%d件产品，现在产品数量 {}".format(self.getName(), products)%tmp)
                    else:
                        products = 0
                        print("{}：消费了%d件产品，现在产品数量 {}".format(self.getName(), products)%oldproducts)
                    condition.notify()
                else:
                    print("{}：剩下0件产品，停止消费。现在产品数量 {}".format(self.getName(), products))
                    condition.wait();
                condition.release()
                time.sleep(1)

if __name__ == "__main__":
    for i in range(2):
        p = Producer()
        p.start()

    for i in range(1):
        c = Consumer()
        c.start()
'''
运行环境:python2.7.12
操作系统:windows7 64bit
多进程解决 两个生产者，一个消费者问题，从任务管理器可以看到一共有4个python.exe在执行。其中3个是生产+消费，还有一个是main。
多进程间无法直接通信，可以用多进程的Queue和Pipe进行数据通信,以及Event变量控制同步通信
'''


'''
import multiprocessing, Queue
import os
import time
from multiprocessing import Process
from time import sleep
from random import randint

# create queue 放置产品
queue = multiprocessing.Queue(10) #进程间数据通信，共用队列

class Producer(multiprocessing.Process):
    def __init__(self, queue,name,e):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.proname = "生产者"+str(name)
        self.e = e

    def run(self):
        while True:
            if self.e.is_set()==False:
                self.e.set()
                p=0
                if(self.queue.qsize()<10):
                    if(self.proname == "生产者0"):
                        self.queue.put('one product')
                        p = 1
                    else:
                        if self.queue.qsize()<9:
                            self.queue.put('one product')
                            self.queue.put('one product')
                            p = 2
                        else:
                            p = 0
                    print self.proname  + '生产%d个产品, 现在队列中的产品数量是: %d' % (p,self.queue.qsize())
                    self.e.clear()
                else:
                    print  '产品队列满了，数量为:%d'%self.queue.qsize()
                    self.e.clear()
                time.sleep(1)

class Consumer(multiprocessing.Process):
    def __init__(self, queue,name,e):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.proname = "消费者"+str(name)
        self.e = e
    def run(self):
        while True:
            if self.e.is_set()==False:
                self.e.set()
                d = self.queue.qsize()
                if d != 0:
                    tmp = randint(1, 5)
                    if(tmp>self.queue.qsize()):
                        tmp=self.queue.qsize()
                    for i in range(tmp):
                        d = self.queue.get()
                    print self.proname + ' 消耗%d个产品,现在队列中产品数量是: %d' % (tmp, self.queue.qsize())
                    self.e.clear()
                else:
                    print  '剩余产品数量: %d' % ( self.queue.qsize())
                    self.e.clear()
                time.sleep(1)


if __name__ == "__main__":
    # create processes
    processed = []
    e = multiprocessing.Event() #Event用来实现进程间同步通信，作为一个互斥锁
    for i in range(2):
        processed.append(Producer(queue,i,e)) #2个生产者
    processed.append(Consumer(queue,1,e))#一个消费者
    # start processes
    for i in range(len(processed)):
        processed[i].start()
    # join processes join()方法可以等待子进程结束后再继续往下运行，通常用于进程间的同步。
    for i in range(len(processed)):
        processed[i].join()

'''