import backend.time_util as tu
from backend.program import Program
from backend.address import Address
from backend.command import Command
from backend.config import config
from backend.schedule import Schedule
from backend.logger import logger
from backend.hardware import hardware
from backend.rl_exception import RlException


class ProgramAlreadyLoaded(RlException):
    pass


class NotProgramLoaded(RlException):
    pass


class NoProgramScheduled(RlException):
    pass


class NoProgramRunning(RlException):
    pass


class NoProgramPaused(RlException):
    pass


class Controller:

    STATE_NOT_LOADED: str = 'not_loaded'
    STATE_LOADED: str = 'loaded'
    STATE_SCHEDULED: str = 'scheduled'
    STATE_RUNNING: str = 'running'
    STATE_PAUSED: str = 'paused'

    _program: Program
    _program_state: str
    _schedule: Schedule

    def __init__(self):
        self._program = None
        self._program_state = self.STATE_NOT_LOADED
        self._schedule = None

    def load_program(self, name: str, json_data: list):
        logger.info(f"Load program {name}", __file__)
        if self._program_state not in (self.STATE_NOT_LOADED,):
            raise ProgramAlreadyLoaded()
        self._program = Program.from_json(name, json_data)
        self._program_state = self.STATE_LOADED
        logger.debug(f"Program {name} loaded", __file__)

    def unload_program(self):
        logger.info("Unload program", __file__)
        if self._program_state not in (self.STATE_LOADED,):
            raise NotProgramLoaded()
        self._unload_program()
        logger.debug("Program unloaded", __file__)

    def schedule_program(self, time: str):
        logger.info(f"Schedule program for {time}", __file__)
        if self._program_state not in (self.STATE_LOADED,):
            raise NotProgramLoaded()
        self._schedule = Schedule(time, self.run_program)
        self._schedule.start()
        self._program_state = self.STATE_SCHEDULED
        logger.debug(f"Program scheduled for {time}", __file__)

    def unschedule_program(self):
        logger.info("Unschedule program", __file__)
        if self._program_state not in (self.STATE_SCHEDULED,):
            raise NoProgramScheduled()
        self._schedule.cancel()
        self._schedule = None
        self._program_state = self.STATE_LOADED
        logger.debug("Program unscheduled", __file__)

    def run_program(self):
        logger.info("Run program", __file__)
        if self._program_state not in (
            self.STATE_LOADED, self.STATE_SCHEDULED
        ):
            raise NotProgramLoaded()
        self._program.run(self._program_finished_callback)
        self._program_state = self.STATE_RUNNING
        logger.debug("Program running", __file__)

    def pause_program(self):
        logger.info("Pause program", __file__)
        if self._program_state not in (self.STATE_RUNNING,):
            raise NoProgramRunning()
        self._program.pause()
        self._program_state = self.STATE_PAUSED
        logger.debug("Program paused", __file__)

    def continue_program(self):
        logger.info("Continue program", __file__)
        if self._program_state not in (self.STATE_PAUSED,):
            raise NoProgramPaused()
        self._program.continue_()
        self._program_state = self.STATE_RUNNING
        logger.debug("Program continued", __file__)

    def stop_program(self):
        logger.info("Stop program", __file__)
        if self._program_state not in (self.STATE_RUNNING, self.STATE_PAUSED):
            raise NoProgramRunning()
        self._program.stop()
        self._unload_program()
        logger.debug("Program stopped", __file__)

    def run_testloop(self):
        logger.info("Run testloop", __file__)
        if self._program_state not in (self.STATE_NOT_LOADED,):
            raise ProgramAlreadyLoaded()
        self._program = Program.testloop_program()
        self._program.run(self._program_finished_callback)
        self._program_state = self.STATE_RUNNING

    def _program_finished_callback(self):
        self._unload_program()
        logger.info("Program finished", __file__)

    def _unload_program(self):
        self._program_state = self.STATE_NOT_LOADED
        self._program = None

    def fire(self, letter: str, number: int):
        logger.info(f"Fire {letter}{number}", __file__)
        if self._program_state not in (self.STATE_NOT_LOADED,):
            raise ProgramAlreadyLoaded()
        address = Address(config.device_id, letter, number)
        command = Command(address, 0, f"manual_fire_command_{address}")
        command.light()

    def get_system_time(self) -> str:
        return tu.get_system_time()

    def get_state(self) -> dict:
        return {
            'controller': {
                'state': self._program_state,
                'system_time': tu.get_system_time(),
            },
            'hardware': hardware.get_state(),
            'config': config.get_state(),
            'schedule': (
                None if self._schedule is None
                else self._schedule.get_state()
            ),
            'program': (
                None if self._program is None
                else self._program.get_state()
            ),
            'update_needed': None
        }


controller = Controller()
