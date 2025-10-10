import argparse
import inspect
import json
import os
import sys
from abc import ABC
from typing import Any

import gvm.connections
import gvm.errors
import gvm.protocols.gmp
import gvm.transforms

import moregvm.exceptions

CREDENTIAL_FILENAME = ".config/moregvm-credentials.json"
DEFAULT_TIMEOUT = 180


class LazyTool(ABC):
    args: dict[str, Any]
    user: str | None
    gmp_hostname: str | None
    gmp: gvm.protocols.gmp.GMPv226 | None

    def __init__(self, args: dict[str, Any]):
        self.args = args
        self.user = None
        self.gmp = None

    def tool_main(self) -> None:
        raise NotImplementedError("Missing tool_main() method.")

    def connect(self):
        """
        establish the connection to greenbone
        """
        if not self.args.get("user") and "GBUSER" in os.environ:
            # TODO temporary for migrating away from the GBUSER env var
            self.errprint("Warning: Use specified via GBUSER env var. Please specify the user with --user instead")
            self.args["user"] = os.environ["GBUSER"]
        if not self.args.get("user"):
            self.errprint("Warning: No user specified, defaulting to 'dev'. Please specify a user with --user")
            self.user = "dev"
        else:
            self.user = self.args["user"]

        cred_json = load_json(CREDENTIAL_FILENAME)
        if self.user not in cred_json["users"]:
            raise moregvm.exceptions.PermanentError(f"unknown user {self.user}")

        self.gmp_hostname = cred_json["hostname"]
        conn = gvm.connections.SSHConnection(hostname=self.gmp_hostname, timeout=self.args["gmp_timeout"])
        gmp = gvm.protocols.gmp.GMPv226(conn, transform=gvm.transforms.EtreeCheckCommandTransform())
        gmp.connect()
        try:
            gmp.authenticate(self.user, cred_json["users"][self.user])
        except gvm.errors.GvmError as e:
            self.errprint("Authentication failed!")
            raise
        self.gmp = gmp

    def output(self, *items: object, sep: str = " ") -> None:
        """
        a simple output function

        The advantage over print() is that it's easier to capture the
        output from other python code that calls the code (by extending
        the class and overriding this function).
        """
        print(*items, sep=sep)

    def errprint(self, *args: object, sep: str = " ", end: str = "\n") -> None:
        """print() but for stderr"""
        print(*args, file=sys.stderr, sep=sep, end=end, flush=True)

    @classmethod
    def help_description(cls) -> str:
        doc = inspect.getdoc(cls)
        if doc:
            return doc.split('\n\n', 1)[0] # first paragraph
        raise NotImplementedError("Missing description. Either override the help_description method or give a docstring")

    @classmethod
    def help_epilog(cls) -> str | None:
        doc = inspect.getdoc(cls)
        if doc:
            arr = doc.split('\n\n', 1)
            if len(arr) == 2:
                return arr[1]
        return None

    @classmethod
    def required_args(cls) -> dict[str, str]:
        """
        These will get added into argparse as positional string arguments
        Return a dict of {name: description}
        """
        return dict()

    @classmethod
    def toggles(cls) -> dict[str, str]:
        """
        Boolean toggles that will get added into argparse as --arg
        Return a dict of {name: description}
        """
        return dict()

    @classmethod
    def option_args(cls) -> dict[str, tuple[str, object]]:
        """
        Optional args which will get added into argparse as --arg=value
        Return a dict of {name: (description, default_value)}
        The special default value ... means that the argument has no default and is required
        """
        return dict()

    @classmethod
    def custom_args(cls, parser: argparse.ArgumentParser) -> None:
        """
        This method is called with the argparse object to allow you to
        tweak it and add custom arguments.
        """
    # TODO config args are optional if present if config, required otherwise

    @classmethod
    def make_argparser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
                description=cls.help_description(),
                epilog=cls.help_epilog(),
                formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("--user", help="Greenbone username", action="store")
        parser.add_argument("--gmp-timeout", help=argparse.SUPPRESS, type=int, default=DEFAULT_TIMEOUT, metavar="TIME")
        for name, description in cls.toggles().items():
            parser.add_argument("--" + name, help=description, action="store_true")
        for name, argtuple in cls.option_args().items():
            description, default = argtuple
            if default == ...:
                parser.add_argument("--" + name, help=description, action="store")
            else:
                parser.add_argument("--" + name, help=description, action="store", default=default)
        for name, description in cls.required_args().items():
            parser.add_argument(name, help=description)
        cls.custom_args(parser)
        return parser

    @classmethod
    def run_from_sysargs(cls) -> None:
        try:
            parser = cls.make_argparser()
            namespace = parser.parse_args()
            args = dict(vars(namespace))
            instance = cls(args)
            instance.tool_main()
        except moregvm.exceptions.TemporaryError as e:
            sys.stderr.write(f"{sys.argv[0].rpartition('/')[-1]}: Error (temporary): {e.message}\nPlease try again\n")
            sys.exit(2)
        except moregvm.exceptions.PermanentError as e:
            sys.stderr.write(f"{sys.argv[0].rpartition('/')[-1]}: Error: {e.message}\n")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.stderr.write(f"{sys.argv[0].rpartition('/')[-1]}: KeyboardInterrupt - exiting.\n")
            sys.excepthook = lambda x,y,z: None # supress stack trace
            raise


class Tool(LazyTool):
    user: str
    gmp: gvm.protocols.gmp.GMPv226
    def __init__(self, args: dict[str, Any]):
        super().__init__(args)
        self.connect()


def load_json(name: str) -> dict[str, Any]:
    path = os.path.join(os.environ['HOME'], name)
    if os.path.exists(path):
        with open(path, 'r') as cfg:
            return json.load(cfg)
    else:
        return {}
