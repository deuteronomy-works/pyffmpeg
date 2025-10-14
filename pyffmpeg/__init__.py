# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:07:19 2020

FFmpeg wrapper for Python. Provides a convenient interface to the FFmpeg executable
for various media processing tasks, including conversion, chaining commands, and
querying FFmpeg binary information.
"""

import os
import shlex
import threading
import logging
from time import sleep
from typing import Optional, List, Union, Callable, Dict, Any
from subprocess import Popen, PIPE, TimeoutExpired, CalledProcessError

from .pseudo_ffprobe import FFprobe
from .misc import Paths, fix_splashes, SHELL, OS_NAME

# --- Global Logging Setup ---
# This part sets up the root 'pyffmpeg' logger.
# It should be configured once when the module is loaded.
# Users can customize this logging further using standard Python logging configuration.

def _setup_global_logging():
    """
    Configures the global 'pyffmpeg' logger with a file handler and a stream handler.
    This function ensures that handlers are not duplicated if called multiple times.
    """
    global_logger = logging.getLogger('pyffmpeg')
    global_logger.setLevel(logging.DEBUG) # Default to DEBUG for internal logs

    # Only add handlers if they haven't been added before
    if not global_logger.handlers:
        try:
            # Paths class might log, so we pass enable_log=False to avoid recursive logging during setup
            log_dir = Paths(enable_log=False).home_path
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'pyffmpeg.log')

            # File handler: logs everything to a file
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setLevel(logging.DEBUG)

            # Stream handler: logs INFO and above to console
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            global_logger.addHandler(fh)
            global_logger.addHandler(ch)
            global_logger.info(f"Global pyffmpeg logger initialized. Log file: {log_file}")
        except Exception as e:
            # Fallback if logging setup fails
            print(f"WARNING: pyffmpeg failed to set up global logging: {e}")
            global_logger.addHandler(logging.NullHandler()) # Prevent 'No handlers could be found for logger "pyffmpeg"' message

_setup_global_logging() # Call once on module import


class FFmpeg():
    """
    FFmpeg wrapper for Python, providing a convenient interface to the FFmpeg executable.
    It includes methods for common media operations like conversion, chaining commands,
    and querying FFmpeg binary information.
    """

    def __init__(self, directory: str = ".", enable_log: bool = True):
        """
        Initializes the FFmpeg wrapper instance.

        :param directory: The default output directory for converted files
                          when relative paths are used. Defaults to the current directory (".").
        :type directory: str
        :param enable_log: Flag to enable or disable instance-specific logging for this FFmpeg instance.
                           Defaults to True. If False, this instance will not emit log messages.
        :type enable_log: bool
        """
        # Instance-specific logger, child of 'pyffmpeg'
        self.logger = logging.getLogger(f'pyffmpeg.FFmpeg.{id(self)}')
        self.enable_log: bool = enable_log

        if not self.enable_log:
            # Disable messages from this specific instance's logger
            self.logger.propagate = False
            self.logger.setLevel(logging.CRITICAL + 1) # Effectively disables logging for this instance

        self.logger.info('FFmpeg instance initialising')

        self.save_dir: str = os.path.abspath(directory) # Resolve absolute path early
        self.logger.info(f"Save directory: {self.save_dir}")

        self.overwrite: bool = True
        self.create_folders: bool = True
        self.loglevels: tuple = (
            'quiet', 'panic', 'fatal', 'error', 'warning',
            'info', 'verbose', 'debug', 'trace')
        self.loglevel: str = 'fatal' # Default FFmpeg loglevel, can be changed by user
        self._log_level_stmt: str = '-loglevel'
        self._over_write_flag: str = '-y' if self.overwrite else '-n'

        # Progress reporting
        self.report_progress: bool = False
        self._in_duration: float = 0.0 # Stored input duration in seconds for progress calculation
        self._progress: int = 0 # Current progress percentage (0-100)
        self.onProgressChanged: Callable[[int], None] = self.progressChangeMock

        # Parameters for method chaining
        self.inputs: List[str] = []
        self.outputs: List[str] = []
        self.chain_string: str = '' # Stores options for chained commands

        # Store Popen instances by an identifier for later control (e.g., quit)
        self._ffmpeg_instances: Dict[str, Popen] = {}

        # Resolve FFmpeg binary path once upon initialization
        try:
            # Pass enable_log to Paths to ensure Paths logging respects instance setting
            self._ffmpeg_file: str = Paths(enable_log=self.enable_log).load_ffmpeg_bin()
            if not os.path.exists(self._ffmpeg_file):
                raise FileNotFoundError(f"FFmpeg binary not found at: {self._ffmpeg_file}")
            self.logger.info(f"FFmpeg binary found: {self._ffmpeg_file}")
        except Exception as e:
            self.logger.critical(f"Failed to load FFmpeg binary: {e}", exc_info=True)
            raise RuntimeError(f"FFmpeg binary not available. Please ensure it's installed and accessible via pyffmpeg's downloader or system PATH. Error: {e}") from e

        self.error: str = '' # Stores the last error message for inspection

    def _get_validated_loglevel(self) -> str:
        """Helper to get a validated FFmpeg loglevel, defaulting to 'fatal' if invalid."""
        if self.loglevel.lower() not in self.loglevels:
            self.logger.warning(f'"{self.loglevel}" is not a valid FFmpeg loglevel flag. Using "fatal" instead.')
            return 'fatal'
        return self.loglevel.lower()

    def _build_command_args(
            self,
            command_parts: List[str],
            include_ffmpeg_bin: bool = True
        ) -> Union[List[str], str]:
        """
        Constructs the final command arguments suitable for Popen,
        handling shell=True/False and quoting.

        :param command_parts: A list of arguments (excluding the ffmpeg binary itself).
        :param include_ffmpeg_bin: Whether to prepend the ffmpeg binary path.
        :return: A list of arguments (for shell=False) or a single string (for shell=True).
        """
        full_command_args: List[str] = []
        if include_ffmpeg_bin:
            full_command_args.append(self._ffmpeg_file)

        full_command_args.extend(command_parts)

        if SHELL:
            # For shell=True, arguments must be a single string.
            # shlex.quote is crucial here to handle spaces/special characters in paths/args.
            quoted_args = [shlex.quote(arg) for arg in full_command_args]
            return " ".join(quoted_args)
        else:
            # For shell=False, arguments must be a list of strings.
            # No manual quoting needed, Popen handles it.
            return full_command_args

    def _execute_ffmpeg_command(self,
                                command_id: str,
                                cmd_args: Union[List[str], str],
                                timeout: Optional[int] = None) -> str:
        """
        Executes an FFmpeg command as a subprocess and handles its output and errors.

        :param command_id: A unique identifier for this command instance. Used for _ffmpeg_instances.
        :param cmd_args: The command arguments (list for shell=False, string for shell=True).
        :param timeout: Optional timeout in seconds for the process to complete.
        :return: The stderr output of the FFmpeg process.
        :raises CalledProcessError: If FFmpeg returns a non-zero exit code.
        :raises TimeoutExpired: If the process times out.
        """
        self.logger.debug(f"Executing command [ID: {command_id}] (Shell={SHELL}): {cmd_args}")
        process: Optional[Popen] = None
        stderr_str = ""
        try:
            process = Popen(cmd_args, shell=SHELL, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self._ffmpeg_instances[command_id] = process

            stdout_data, stderr_data = process.communicate(timeout=timeout)
            stderr_str = stderr_data.decode('utf-8', errors='ignore')

            if process.returncode != 0:
                self.error = f"FFmpeg command failed with exit code {process.returncode}.\nCommand: {cmd_args}\nStderr: {stderr_str}"
                self.logger.error(self.error)
                raise CalledProcessError(process.returncode, cmd_args, stdout=stdout_data, stderr=stderr_data)
            else:
                self.error = '' # Clear previous error on success
                self.logger.info(f"FFmpeg command [ID: {command_id}] executed successfully.")
            return stderr_str
        except TimeoutExpired:
            if process:
                process.kill()
                # Communicate again after kill to get any remaining output
                stdout_data, stderr_data = process.communicate()
                stderr_str = stderr_data.decode('utf-8', errors='ignore')
                self.logger.error(f"FFmpeg command [ID: {command_id}] timed out and was killed.\nCommand: {cmd_args}\nStderr: {stderr_str}")
            self.error = f"FFmpeg command [ID: {command_id}] timed out after {timeout} seconds."
            raise
        except CalledProcessError:
            # This exception is already handled and logged above. Just re-raise.
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during FFmpeg command [ID: {command_id}]: {e}\nCommand: {cmd_args}", exc_info=True)
            self.error = f"Error during FFmpeg execution: {e}"
            raise
        finally:
            if command_id in self._ffmpeg_instances:
                del self._ffmpeg_instances[command_id] # Clean up instance reference

    def convert(self, input_file: str, output_file: str) -> str:
        """
        Converts an input file to the specified output file using FFmpeg.
        This is a direct, non-chained conversion method.

        :param input_file: Path to the input media file. Can be a local path or URL.
        :type input_file: str
        :param output_file: Path to the desired output media file. If a relative path
                            is provided, `self.save_dir` will be used as the base.
        :type output_file: str
        :return: The absolute path of the generated output file.
        :rtype: str
        :raises CalledProcessError: If the FFmpeg conversion process encounters an error.
        :raises FileNotFoundError: If required output directories cannot be created.
        """
        self.logger.info('Starting convert function')
        
        # Resolve output path
        out_path_abs = os.path.abspath(output_file) if os.path.isabs(output_file) else \
                       os.path.join(self.save_dir, output_file)
        
        out_dir = os.path.dirname(out_path_abs)
        if not os.path.exists(out_dir) and self.create_folders:
            try:
                os.makedirs(out_dir, exist_ok=True) # Use exist_ok=True for idempotence
                self.logger.info(f"Created output directory: {out_dir}")
            except OSError as e:
                self.logger.error(f"Failed to create output directory {out_dir}: {e}", exc_info=True)
                raise FileNotFoundError(f"Could not create output directory: {out_dir}") from e

        self.logger.info(f"Output file: {out_path_abs}")
        self.logger.info(f"Input file: {input_file}")

        # Construct options list
        options = []
        options.append(self._over_write_flag) # Always add overwrite/no-overwrite flag
        
        validated_loglevel = self._get_validated_loglevel()
        options.extend([self._log_level_stmt, validated_loglevel])
        
        options.extend(["-i", input_file, out_path_abs])

        if self.report_progress:
            try:
                # FFprobe on the input file to get its total duration for progress calculation
                f_probe = FFprobe(input_file, enable_log=self.enable_log)
                self._in_duration = f_probe.duration_seconds
                self.logger.info(f"Input duration for progress monitoring: {self._in_duration:.2f} seconds.")
                if self._in_duration > 0:
                    # Start monitoring the output file in a background thread
                    self.monitor(out_path_abs)
                else:
                    self.logger.warning(f"Could not determine input duration for '{input_file}', progress monitoring will be limited.")
                    # Keep report_progress=True but understand progress might be unreliable
            except Exception as e:
                self.logger.error(f"Failed to probe input file '{input_file}' for duration: {e}. Progress monitoring might be inaccurate.", exc_info=True)
                # Do not set report_progress=False here, as the user enabled it. Just warn.

        command_args = self._build_command_args(options)
        
        try:
            self._execute_ffmpeg_command('convert', command_args)
            self.logger.info('Conversion Done')
        except CalledProcessError as e:
            self.logger.error(f"FFmpeg conversion failed during convert(): {e.stderr.decode('utf-8', errors='ignore')}")
            raise # Re-raise the exception for the caller
        finally:
            self.progress = 100 # Ensure progress is set to 100% on completion or error
            if self.report_progress and 'convert' in self._ffmpeg_instances:
                # Ensure the monitoring thread is aware the main process has finished
                # This check might be redundant if _execute_ffmpeg_command cleans up.
                pass # The _monitor loop itself checks ffmpeg_proc.poll()

        return out_path_abs

    def clip(self, start: Union[int, float, str], end: Union[int, float, str]) -> 'FFmpeg':
        """
        Adds `-ss` (start time) and `-to` (end time) options to the command chain
        for clipping media. These options are typically placed *before* the input file specification
        to enable faster seeking.

        :param start: The start timestamp for the clip. Can be an integer (seconds),
                      float (seconds), or a time string (e.g., 'HH:MM:SS', '00:00:10').
        :type start: Union[int, float, str]
        :param end: The end timestamp for the clip. Can be an integer (seconds),
                    float (seconds), or a time string (e.g., 'HH:MM:SS', '00:00:20').
        :type end: Union[int, float, str]
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        :raises ValueError: If clip is called after inputs are already defined in a way that
                            prevents correct insertion of -ss and -to.
        """
        self.logger.info(f"Adding clip options (-ss {start}, -to {end})")
        
        time_options = f"-ss {start} -to {end}"

        # Attempt to insert time options before the first input (-i)
        # This is a heuristic; a more robust chaining mechanism would manage an ordered list of options.
        if " -i " in self.chain_string:
            # Split at the first occurrence of " -i "
            parts = self.chain_string.split(" -i", 1)
            self.chain_string = f"{parts[0]} {time_options} -i{parts[1]}".strip()
            self.logger.debug(f"Inserted clip options before first input. New chain: {self.chain_string}")
        elif self.inputs:
            # Inputs were set but not with the " -i " string (e.g., via a different mechanism)
            # This case is less ideal for -ss -to
            self.logger.warning("Clip options (-ss, -to) ideally precede '-i'. Inputs already defined; options appended.")
            self.chain_string += f" {time_options}"
        else:
            # No inputs defined yet, just append; they will naturally precede -i when input() is called
            self.chain_string += f" {time_options}"
            self.logger.debug(f"Appended clip options, assuming input() will be called next. New chain: {self.chain_string}")

        return self

    def duration(self, duration: Union[int, float, str]) -> 'FFmpeg':
        """
        Adds the `-t` option to the command chain to specify the duration of the output.
        This option is typically placed before the output file.

        :param duration: The desired duration. Can be an integer (seconds),
                         float (seconds), or a time string (e.g., 'HH:MM:SS', '00:00:30').
        :type duration: Union[int, float, str]
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        self.logger.info(f"Adding output duration option (-t {duration})")
        self.chain_string += f" -t {duration}"
        return self

    def run(self) -> str:
        """
        Executes the FFmpeg command that has been constructed using the
        chained methods (e.g., `input()`, `output()`, `clip()`, `duration()`, etc.).

        :return: The stderr output if the FFmpeg command executes successfully.
        :rtype: str
        :raises CalledProcessError: If the FFmpeg command encounters an error.
        """
        self.logger.info("Executing chained FFmpeg command via run()")

        # Build options list from chain_string, injecting mandatory flags
        # Use posix=False for shlex.split to better handle Windows-style paths
        options: List[str] = shlex.split(self.chain_string, posix=False)

        # Ensure overwrite flag is present
        if self._over_write_flag not in options:
            options.insert(0, self._over_write_flag)

        # Ensure loglevel statement is present
        validated_loglevel = self._get_validated_loglevel()
        if self._log_level_stmt not in options:
            options.insert(0, validated_loglevel)
            options.insert(0, self._log_level_stmt)
        else:
            # If loglevel is already present in `options`, ensure it's the validated one.
            # This prevents user-supplied invalid loglevels from propagating.
            try:
                idx = options.index(self._log_level_stmt)
                if idx + 1 < len(options) and options[idx + 1].lower() not in self.loglevels:
                    self.logger.warning(f"Overriding invalid loglevel '{options[idx + 1]}' with '{validated_loglevel}' for chained command.")
                    options[idx + 1] = validated_loglevel
            except ValueError:
                pass # Should not happen if _log_level_stmt is in options

        # Build the final command arguments
        command_args = self._build_command_args(options)

        try:
            stderr_output = self._execute_ffmpeg_command('run_chain', command_args)
            self.logger.info('Chained operation Done')
        except CalledProcessError as e:
            self.logger.error(f"FFmpeg chained command failed during run(): {e.stderr.decode('utf-8', errors='ignore')}")
            raise # Re-raise the exception
        finally:
            # Wipe all chain string data after execution to allow for fresh commands
            self.chain_string = ''
            self.inputs = []
            self.outputs = []
        return stderr_output

    def input(
            self, *inputs: str,
            stream_maps: Optional[List[str]] = None,
            rate: Union[int, float] = 0) -> 'FFmpeg':
        """
        Adds one or more input files to the FFmpeg command chain.
        Input options like `-r` (input frame rate) are placed before the `-i` flag.

        :param inputs: Variable number of paths to input media files.
                       Can be local paths or URLs.
        :type inputs: str
        :param stream_maps: A list of stream mappings (e.g., ['0:1', '0:0']) applied
                            after input. These are typically global or output-specific. Defaults to None.
        :type stream_maps: Optional[List[str]]
        :param rate: The input frame rate (adds `-r` option before the `-i` for *each* input).
                     Defaults to 0 (no explicit rate).
        :type rate: Union[int, float]
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        self.logger.info(f"Adding inputs: {inputs}")
        
        input_segment_parts: List[str] = []

        for input_file in inputs:
            # Input options like -r typically go before -i for input-specific settings
            if rate:
                input_segment_parts.append(f"-r {rate}")

            input_f = fix_splashes([input_file])[0] # Standardize path separators
            input_segment_parts.append(f"-i {shlex.quote(input_f)}") # Quote input paths for robustness
            self.logger.debug(f"Input file added to chain: {input_f}")
            self.inputs.append(input_f) # Store for internal reference

        # Append input segment to the main chain string
        self.chain_string += " " + " ".join(input_segment_parts)

        # mapping arguments: "-map 0:1 -map 0:0"
        if stream_maps:
            map_args = [f"-map {m}" for m in stream_maps]
            self.chain_string += " " + " ".join(map_args)
            self.logger.debug(f"Added input stream maps: {stream_maps}")

        return self

    def output(self, *outputs: str) -> 'FFmpeg':
        """
        Adds one or more output files to the FFmpeg command chain.
        Output-specific options (like `-t`, `-b`, `-c:v`, etc.) should typically
        be specified *before* the corresponding output file.

        :param outputs: Variable number of paths to output media files.
                        If relative paths are provided, `self.save_dir`
                        will be used as the base.
        :type outputs: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        self.logger.info(f"Adding outputs: {outputs}")

        processed_outputs = []
        for output_file in outputs:
            out = os.path.abspath(output_file) if os.path.isabs(output_file) else \
                  os.path.join(self.save_dir, output_file)

            out_path = os.path.dirname(out)
            if not os.path.exists(out_path) and self.create_folders:
                try:
                    os.makedirs(out_path, exist_ok=True)
                    self.logger.debug(f"Created output directory for {out}: {out_path}")
                except OSError as e:
                    self.logger.error(f"Failed to create output directory {out_path}: {e}", exc_info=True)
                    # Log the error but allow FFmpeg to attempt output, as it might handle missing dirs differently
                    pass

            processed_outputs.append(shlex.quote(out)) # Quote output paths for robustness
            self.logger.debug(f"Output file added to chain: {out}")
            self.outputs.append(out) # Store for internal reference

        # Append output files to the chain string
        self.chain_string += " " + " ".join(processed_outputs)
        return self

    def bitrate(self, value: Union[int, str], stream_specifier: str = "") -> 'FFmpeg':
        """
        Adds the `-b` (bitrate) or `-b:<specifier>` option to the command chain.

        :param value: The bitrate value (e.g., '1M' for 1 Mbit/s, '200k' for 200 kbit/s, or an integer in bits/s).
        :type value: Union[int, str]
        :param stream_specifier: Optional stream specifier ('a' for audio, 'v' for video, 's' for subtitle).
                          If empty, applies to all streams or the context implies. Defaults to "".
        :type stream_specifier: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        stream_specifier = stream_specifier.lower()
        if stream_specifier in ['a', 'v', 's']:
            self.chain_string += f" -b:{stream_specifier} {value}"
        else:
            self.chain_string += f" -b {value}"
        self.logger.debug(f"Added bitrate option: -b:{stream_specifier if stream_specifier else ''} {value}")
        return self

    def aspect_ratio(self, value: str, stream_specifier: str = "") -> 'FFmpeg':
        """
        Adds the `-aspect[:stream_specifier]` option to the command chain for setting video aspect ratio.

        :param value: The aspect ratio (e.g., '16:9', '4:3', or '1.777').
        :type value: str
        :param stream_specifier: Optional stream specifier (e.g., 'v:0'). Defaults to "".
        :type stream_specifier: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        if stream_specifier:
            specifier_str = f":{stream_specifier}"
        else:
            specifier_str = ""
        self.chain_string += f" -aspect{specifier_str} {value}"
        self.logger.debug(f"Added aspect ratio option: -aspect{specifier_str} {value}")
        return self

    def filter(self, value: str, stream_specifier: str = "") -> 'FFmpeg':
        """
        Adds the `-filter` or `-filter:<stream_specifier>` option to the command chain
        for applying filter graphs. The filter graph string is automatically quoted.

        :param value: The filter graph string (e.g., 'scale=w=1280:h=720').
        :type value: str
        :param stream_specifier: Optional stream specifier ('a' for audio, 'v' for video).
                          If empty, applies to all streams or the context implies. Defaults to "".
        :type stream_specifier: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        stream_specifier = stream_specifier.lower()
        if stream_specifier in ['a', 'v']:
            self.chain_string += f" -filter:{stream_specifier} {shlex.quote(value)}"
        else:
            self.chain_string += f" -filter {shlex.quote(value)}"
        self.logger.debug(f"Added filter option: -filter:{stream_specifier if stream_specifier else ''} {value}")
        return self

    def format(self, value: str) -> 'FFmpeg':
        """
        Adds the `-f` (force format) option to the command chain.
        This forces the output file format. This option typically
        comes before the output file name.

        :param value: The desired format name (e.g., 'mp4', 'webm', 'hls').
        :type value: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        self.chain_string += f" -f {value}"
        self.logger.debug(f"Added format option: -f {value}")
        return self

    def channels(self, value: int, stream_specifier: str = "") -> 'FFmpeg':
        """
        Adds the `-ac` (audio channels) option to the command chain.
        Note: FFmpeg uses `-ac` for audio channels. There isn't a direct `-vc` for video channels;
        video channel manipulation is typically done via video filters (e.g., `channelmap`).

        :param value: The number of channels.
        :type value: int
        :param stream_specifier: Optional stream specifier ('a' for audio, 'v' for video).
                          If 'a' is specified, it adds `-ac`. For 'v' or empty,
                          a warning is issued and `-ac` is used for ambiguity unless explicitly 'v'.
        :type stream_specifier: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        stream_specifier = stream_specifier.lower()
        if stream_specifier == 'a':
            self.chain_string += f" -ac {value}"
        elif stream_specifier == 'v':
            self.logger.warning("'-vc' is not a standard FFmpeg option for video channels. Consider using video filters for video channel manipulation.")
            # For strict adherence, one might prevent this or error. For flexibility, we allow but warn.
            self.chain_string += f" -c:v {value}" # This is likely wrong for channels, but closest interpreted
        else:
            # If no specifier, assume audio channels as it's the most common use
            self.chain_string += f" -ac {value}"
            self.logger.debug(f"Ambiguous channel option '{value}' defaulting to audio channels (-ac). Consider using stream_specifier='a'.")

        self.logger.debug(f"Added channels option: {value}, specifier: {stream_specifier}")
        return self

    def rate(self, value: Union[int, float], stream_specifier: str = "") -> 'FFmpeg':
        """
        Adds the `-r` (output frame rate for video) or `-ar` (audio sample rate) option to the command chain.
        For input frame rate, use the `rate` parameter in `input()`.

        :param value: The rate value (frames per second for video, samples per second for audio).
        :type value: Union[int, float]
        :param stream_specifier: Optional stream specifier ('a' for audio sample rate, 'v' for video frame rate).
                          If empty, applies to general output video frame rate. Defaults to "".
        :type stream_specifier: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        stream_specifier = stream_specifier.lower()
        if stream_specifier == 'a':
            self.chain_string += f" -ar {value}"
        elif stream_specifier == 'v':
            self.chain_string += f" -r {value}" # -r usually for video frame rate
        else:
            # Default to video frame rate if no specifier provided for 'rate' method
            self.chain_string += f" -r {value}"
            self.logger.debug(f"Ambiguous rate option '{value}' defaulting to video frame rate (-r). Consider using stream_specifier='v' or 'a'.")

        self.logger.debug(f"Added rate option: {value}, specifier: {stream_specifier}")
        return self

    def codec(self, value: str = 'copy', stream_specifier: str = "") -> 'FFmpeg':
        """
        Adds the `-c` (codec) or `-c:<stream_specifier>` option to the command chain.

        :param value: The codec name (e.g., 'libx264', 'aac', 'copy').
                      Defaults to 'copy'.
        :type value: str
        :param stream_specifier: Optional stream specifier ('v' for video, 'a' for audio, 's' for subtitle).
                          If empty, applies to all streams. Defaults to "".
        :type stream_specifier: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        stream_specifier = stream_specifier.lower()
        if stream_specifier in ['v', 'a', 's']:
            self.chain_string += f" -c:{stream_specifier} {value}"
        else:
            self.chain_string += f" -c {value}"
        self.logger.debug(f"Added codec option: -c:{stream_specifier if stream_specifier else ''} {value}")
        return self

    def disable(self, stream_type: str) -> 'FFmpeg':
        """
        Adds options to disable specific streams in the output.

        :param stream_type: The type of stream to disable: 'v' for video (-vn),
                      'a' for audio (-an), or 's' for subtitles (-sn). Case-insensitive.
        :type stream_type: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        stream_type = stream_type.lower()
        if stream_type in ['v', 'a', 's']:
            self.chain_string += f' -{stream_type}n'
            self.logger.debug(f"Disabled stream type: -{stream_type}n")
        else:
            self.logger.warning(f"Invalid stream type '{stream_type}' for disable(). Must be 'v', 'a', or 's'.")
        return self

    def map(self, value: str) -> 'FFmpeg':
        """
        Adds the `-map` option to the command chain for explicit stream selection.
        This is distinct from the `stream_maps` parameter in the `input()` method,
        which applies a map to a specific input during its definition. This `map()`
        method adds a general `-map` option to the command.

        :param value: The stream mapping string (e.g., '0:0', '0:v', '[out]').
        :type value: str
        :return: The FFmpeg instance, allowing for method chaining.
        :rtype: FFmpeg
        """
        self.chain_string += f' -map {value}'
        self.logger.debug(f"Added general map option: -map {value}")
        return self

    def get_ffmpeg_bin(self) -> str:
        """
        Returns the full path to the FFmpeg executable distributed with pyffmpeg.

        :return: The absolute path to the FFmpeg binary.
        :rtype: str
        """
        self.logger.info("Retrieving FFmpeg binary path.")
        return self._ffmpeg_file

    def get_fps(self, input_file: str) -> float:
        """
        Retrieves the frames per second (FPS) rate of a given input file
        by using the internal `FFprobe` utility.

        :param input_file: Path to the input media file.
        :type input_file: str
        :return: The FPS rate of the video stream, or 0.0 if not found/applicable.
        :rtype: float
        """
        self.logger.info(f"Retrieving FPS for input file: {input_file}")
        try:
            fprobe = FFprobe(input_file, enable_log=self.enable_log)
            fps_str = fprobe.fps # e.g., "25/1", "30000/1001", or just "25"
            if fps_str:
                if '/' in fps_str:
                    num, den = map(int, fps_str.split('/'))
                    return float(num / den) if den != 0 else 0.0
                return float(fps_str)
            return 0.0 # No FPS found
        except Exception as e:
            self.logger.error(f"Failed to get FPS for '{input_file}': {e}", exc_info=True)
            return 0.0

    def monitor(self, output_file_path: str) -> None:
        """
        Starts a background thread to monitor the progress of a conversion
        by repeatedly probing the output file. This method is generally
        called internally by `convert()` if `report_progress` is enabled.

        Note: This monitoring approach relies on repeatedly calling FFprobe
        on the output file, which can be resource-intensive for very short
        intervals or very large files. For more efficient monitoring,
        parsing FFmpeg's `stderr` output directly for progress indicators
        is generally preferred, but requires more complex parsing logic.

        :param output_file_path: The path to the output file being monitored.
        :type output_file_path: str
        """
        if not self.report_progress:
            self.logger.debug("Progress monitoring is disabled.")
            return

        m_thread = threading.Thread(target=self._monitor, args=[output_file_path], daemon=True)
        m_thread.start()
        self.logger.info(f"Started progress monitoring thread for {output_file_path}")

    def _monitor(self, output_file_path: str) -> None:
        """
        Internal method for the progress monitoring thread.
        It updates `self.progress` which in turn triggers `onProgressChanged`.
        The thread continues until the associated FFmpeg process is detected as finished.

        :param output_file_path: The path to the output file being monitored.
        :type output_file_path: str
        """
        self.logger.debug(f'Monitoring thread started for {output_file_path}')
        
        # Give FFmpeg some time to start writing the file
        sleep(2)
        
        current_output_duration = 0.0
        
        # Look up the Popen instance associated with 'convert'
        # This assumes 'monitor' is primarily called by the 'convert' method
        # for a single, long-running process.
        ffmpeg_proc: Optional[Popen] = self._ffmpeg_instances.get('convert') 

        while True:
            # Check if the FFmpeg process is still alive. If not, monitoring should stop.
            if ffmpeg_proc and ffmpeg_proc.poll() is not None:
                self.logger.debug(f"FFmpeg process for 'convert' (PID: {ffmpeg_proc.pid}) has finished. Stopping monitor.")
                break # Exit monitoring loop if FFmpeg process is done or finished

            if not os.path.exists(output_file_path):
                self.logger.debug(f"Output file '{output_file_path}' not yet created by FFmpeg. Waiting...")
                sleep(0.5)
                continue

            try:
                # Re-instantiate FFprobe to get fresh metadata on the output file
                f_probe = FFprobe(output_file_path, enable_log=self.enable_log)
                new_duration = f_probe.duration_seconds
                
                if new_duration is not None and new_duration > current_output_duration:
                    current_output_duration = new_duration
                    if self._in_duration > 0: # Avoid ZeroDivisionError
                        progress_percent = int((current_output_duration / self._in_duration) * 100)
                        self.progress = min(progress_percent, 99) # Cap at 99% until conversion truly finishes
                    else:
                        # If input duration is unknown, progress will be 0, or could be based on file size if feasible.
                        # For now, if input duration is 0, progress remains 0 (or some other heuristic).
                        self.progress = 0 
                
            except Exception as e:
                self.logger.debug(f"Error probing file '{output_file_path}' during monitoring: {e}")
            
            sleep(1) # Probe every 1 second to balance responsiveness and resource usage

        # Final update to 100% when the process is confirmed finished
        self.progress = 100
        self.logger.info(f'Monitoring thread for {output_file_path} finished.')


    def options(self, opts: Union[List[str], str]) -> str:
        """
        Allows passing raw FFmpeg command-line options directly to the executable.
        This method is for one-off commands and does not participate in method chaining.

        :param opts: A string or a list of strings representing the FFmpeg
                     command-line arguments (excluding the `ffmpeg` executable itself).
                     e.g., `['-i', 'input.mp4', 'output.mp3']` or `'-i input.mp4 output.mp3'`.
        :type opts: Union[List[str], str]
        :return: The stderr output if the FFmpeg command executes successfully.
        :rtype: str
        :raises CalledProcessError: If the FFmpeg command encounters an error.
        """
        self.logger.info("Executing raw FFmpeg options via options()")

        options_list: List[str]
        if isinstance(opts, str):
            options_list = shlex.split(opts, posix=False)
        else:
            options_list = fix_splashes(opts) # Use fix_splashes for input list paths

        # Ensure overwrite flag is present if not already in user options
        if self._over_write_flag not in options_list:
            options_list.insert(0, self._over_write_flag)

        # Ensure loglevel statement is present. This overrides user-supplied loglevels
        # that are not recognized by FFmpeg or if loglevel is not present.
        validated_loglevel = self._get_validated_loglevel()
        if self._log_level_stmt not in options_list:
            options_list.insert(0, validated_loglevel)
            options_list.insert(0, self._log_level_stmt)
        else:
            try:
                idx = options_list.index(self._log_level_stmt)
                if idx + 1 < len(options_list) and options_list[idx + 1].lower() not in self.loglevels:
                    self.logger.warning(f"Overriding invalid loglevel '{options_list[idx + 1]}' with '{validated_loglevel}' for raw options command.")
                    options_list[idx + 1] = validated_loglevel
            except ValueError:
                pass # Should not happen if _log_level_stmt is in options_list

        command_args = self._build_command_args(options_list)

        try:
            stderr_output = self._execute_ffmpeg_command('raw_options', command_args)
            self.logger.info('Raw options command Done')
        except CalledProcessError as e:
            self.logger.error(f"FFmpeg raw options command failed: {e.stderr.decode('utf-8', errors='ignore')}")
            raise # Re-raise the exception
        return stderr_output

    @property
    def progress(self) -> int:
        """
        Gets the current progress percentage of an ongoing conversion being monitored.

        :return: The progress as an integer between 0 and 100.
        :rtype: int
        """
        return self._progress

    @progress.setter
    def progress(self, percent: int) -> None:
        """
        Sets the current progress percentage and triggers the `onProgressChanged` callback.
        Ensures the percentage is within the valid range [0, 100].

        :param percent: The progress percentage (0-100).
        :type percent: int
        """
        if 0 <= percent <= 100:
            self._progress = percent
            self.onProgressChanged(self._progress)
        else:
            self.logger.warning(f"Attempted to set progress to invalid value: {percent}. Progress must be between 0 and 100.")

    def progressChangeMock(self, progress: int) -> None:
        """
        A mock callback function for `onProgressChanged` when no custom handler is provided.
        It simply consumes the progress value and does nothing.

        :param progress: The current progress percentage.
        :type progress: int
        """
        pass

    def quit(self, function_id: Optional[str] = '') -> None:
        """
        Terminates one or all currently running FFmpeg subprocesses started by this instance.
        Attempts a graceful shutdown first by sending 'q', then force kills if it times out.

        :param function_id: The identifier of the method that started the FFmpeg process to terminate
                            (e.g., 'convert', 'run_chain', 'raw_options'). If an empty string (default),
                            all running processes managed by this instance will be terminated.
        :type function_id: Optional[str]
        """
        self.logger.info(f'Inside Quit. Function ID: {function_id if function_id else "all"}')

        instances_to_quit: Dict[str, Popen]
        if function_id:
            # Only consider the specified instance if it exists and is still running
            proc = self._ffmpeg_instances.get(function_id)
            instances_to_quit = {function_id: proc} if proc and proc.poll() is None else {}
        else:
            # Iterate over a copy of the dictionary to allow modification during iteration
            instances_to_quit = {name: proc for name, proc in self._ffmpeg_instances.items() if proc.poll() is None}

        for func_name, proc_instance in instances_to_quit.items():
            if proc_instance and proc_instance.poll() is None: # Double-check it's still running
                self.logger.info(f'Attempting to terminate process for function ID: {func_name} (PID: {proc_instance.pid})')
                try:
                    # Attempt graceful shutdown by sending 'q' to stdin
                    # FFmpeg often reacts to 'q' + newline
                    proc_instance.communicate(input=b'q\n', timeout=1) 
                    proc_instance.wait(timeout=1) # Wait for process to finish
                    self.logger.info(f"Process for '{func_name}' (PID: {proc_instance.pid}) terminated gracefully.")
                except TimeoutExpired:
                    self.logger.warning(f"FFmpeg process for '{func_name}' (PID: {proc_instance.pid}) did not terminate cleanly within 1s; killing.")
                    proc_instance.kill() # Force kill if it doesn't respond
                    proc_instance.wait() # Wait for it to be truly dead to avoid zombie processes
                except Exception as e:
                    self.logger.error(f"Error terminating process for '{func_name}' (PID: {proc_instance.pid}): {e}", exc_info=True)
                finally:
                    # Clean up the reference to the Popen object regardless of how it terminated
                    if func_name in self._ffmpeg_instances:
                        del self._ffmpeg_instances[func_name]
            else:
                self.logger.debug(f"Process for '{func_name}' was already terminated or not found.")
                if func_name in self._ffmpeg_instances:
                    del self._ffmpeg_instances[func_name]

        if not function_id: # If quitting all, ensure the dictionary is empty
            self._ffmpeg_instances.clear()
            self.logger.info("All FFmpeg instances managed by this object have been terminated.")