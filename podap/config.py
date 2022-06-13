import argparse
import os
import sys
from typing import Optional


class Config:
    INSTANCE = None  # type: Optional['Config']

    def __init__(self, working_directory: str, pause_duration: int, pause_text: str, borderless: bool):
        self.working_directory = working_directory
        self.pause_text = pause_text
        self.pause_duration = pause_duration
        self.borderless = borderless

    @staticmethod
    def _get_default_working_dir():
        binary_dir = os.path.dirname(sys.argv[0])
        if sys.platform == 'darwin' and 'Contents/MacOS' in binary_dir:
            # We are inside an macOS bundles
            binary_dir = os.path.abspath(os.path.join(binary_dir, '..', '..', '..'))
            pass
        return os.path.join(binary_dir, 'input')

    @staticmethod
    def from_args() -> 'Config':
        parser = argparse.ArgumentParser(description='Pomodoro Day Planner (podap)')
        parser.add_argument('--working-directory', '-wd', type=str, required=False,
                            default=Config._get_default_working_dir(),
                            help='Working directory, containing a list of text files, '
                                 'each containing the day '
                                 'schedule (e.g: 0_mo.txt)')
        parser.add_argument('--pause-duration', '-pd', type=int, required=False, default=15,
                            help='Pause duration, in minutes. The app is currently supports only the hourly regime!')
        parser.add_argument('--pause-text', '-pt', type=str, required=False, default='PAUSE',
                            help='Text for "pause" entries')
        parser.add_argument('--borderless', '-b', action='store_true', required=False, default=False,
                            help='Use a borderless window')

        args = parser.parse_args()
        return Config(working_directory=args.working_directory, pause_duration=args.pause_duration,
                      pause_text=args.pause_text, borderless=args.borderless)
