#!/usr/bin/env python3
# Thread_Racing.py
# Author: Mark DiVelbiss
# The goal of this program is to run multiple threads simultaneously and have them "race" by
# attempting to roll a six sided dice and get a 6.
# Bad rolls lead to time penalties whereas good rolls allow the thread to advance to the next stage.
from threading import Thread, Lock
import time
import random


# This is the class representing each thread. It only has the run method.
class RaceThread(Thread):
    def run(self):
        # Initiate stage and obtain an id from host
        stage = STAGE_START
        thread_id = host.register_thread(stage)
        # Loop until you've reached the winning stage
        while stage < STAGE_WIN:
            time.sleep(THREAD_SLEEP_TIME)  # Sleep between rolls
            guess = random.randint(1, DICE_ROLL + 1)
            if guess == DICE_ROLL:  # If roll is the max roll, go up a stage
                stage += 1
                host.update_thread_stage(thread_id, stage)
            if host.has_winner():  # Someone else one, so break loop and end thread
                break


# The host class tracks the progress of all active RaceThreads
# Host class does not police the threads as they tell the host whether or not they've advanced
class Host:
    def __init__(self):
        self.thread_stage = []
        self.winner = -1

    def has_winner(self):  # boolean return method for determining if a winner exists yet
        return self.winner >= 0

    def get_winner(self):  # Returns integer of the thread_id of the winner
        return self.winner

    def register_thread(self, stage):  # Assigns an integer id to RaceThreads using mutex
        mutex.acquire()  # Prevents id overlap and any thread from starting before all threads have been created
        thread_id = len(self.thread_stage)
        self.thread_stage.append(stage)
        mutex.release()
        return thread_id;

    def update_thread_stage(self, thread_id, stage):  # Updates the current stage of each RaceThread based on input
        mutex.acquire()
        if self.thread_stage[thread_id] < stage:
            self.thread_stage[thread_id] = stage
            if stage >= STAGE_WIN and not self.has_winner():
                self.winner = thread_id  # You've passed win stage before anyone else, YOU WIN!
        mutex.release()

    def post_thread_status(self):  # Post in graphical format the current setup of the race track
        print()
        if self.has_winner():
            print("FINAL")  # Added title for final results
        for j in range(len(self.thread_stage)):
            progress = PROGRESS_CHAR * self.thread_stage[j]  # Draws a representation of a thread's current stage
            remaining = REMAINING_CHAR * (STAGE_WIN - self.thread_stage[j])  # Draws a representation of the stages left
            print("T{0:d}|{1}{2}|".format(j, progress, remaining))


# Initialize global variables
STAGE_START = 0  # Starting stage or "square" for each thread, should be 0
STAGE_WIN = 30  # Final stage for each thread which is the win condition
DICE_ROLL = 6  # The number of sides the rolled dice has. The chance to progress on each roll is 1/DICE_ROLL
THREAD_COUNT = 5  # Number of threads race concurrently
THREAD_SLEEP_TIME = 0.1  # Amount of time in seconds a thread will wait before rolling again
POST_SLEEP_TIME = 0.5  # Amount of time main will wait before posting the current results again
PROGRESS_CHAR = '='  # The character showing progress on the race track
REMAINING_CHAR = ' '  # The character showing the part of the track a thread still has to go through
mutex = Lock()  # The only mutual exclusion lock for protecting the host's members
host = Host()  # The host who manages result data and declares a winner

if __name__ == '__main__':
    # Grab the lock, then initiate threads, then start them as they won't actually begin until the lock is released
    mutex.acquire()
    for i in range(THREAD_COUNT):
        mythread = RaceThread()
        mythread.start()
    mutex.release()

    time.sleep(POST_SLEEP_TIME)  # Wait to give threads a chance to register

    # Loop and display host's results until a winner is declared
    while not host.has_winner():
        host.post_thread_status()
        time.sleep(POST_SLEEP_TIME)

    # Announce the winner clearly then end program
    host.post_thread_status()
    print("Thread {0:d} wins!".format(host.get_winner()))
