from datetime import datetime


class Stopwatch:
    def __init__(self):
        self.null = datetime(2000, 1, 1, 0, 0, 0)
        self.start_time = self.null
        self.finish_time = self.null
        self.last_round = self.null
        self.rounds = 0

    def active(self):
        if self.start_time != self.null and self.finish_time == self.null:
            return True
        else:
            return False

    def start(self):
        self.start_time = datetime.now()
        self.finish_time = self.null
        self.last_round = self.null
        self.rounds = 0
        return self

    def round(self):
        last_round = self.last_round if self.last_round != self.null else self.start_time
        round = datetime.now()
        duration1 = round.timestamp() - last_round.timestamp()
        duration2 = round.timestamp() - self.start_time.timestamp()
        self.last_round = round
        self.rounds += 1
        return duration1, duration2

    def finish(self):
        self.finish_time = datetime.now()
        duration = self.finish_time.timestamp() - self.start_time.timestamp()
        return duration
