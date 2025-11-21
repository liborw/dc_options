from dataclasses import dataclass

from dc_options import Options, option


@dataclass
class Serve(Options):
    host: str = option(
        default="127.0.0.1",
        description="Bind address",
    )
    port: int = option(
        default=8080,
        min=1024,
        max=65535,
        description="HTTP port",
    )


@dataclass
class App(Options):
    workers: int = option(default=2, min=1, description="Number of worker processes")
    log_level: str = option(
        default="info",
        choices=["debug", "info", "warning", "error"],
        description="Application log level",
    )
    serve: Serve = option(default_factory=Serve)


def build_config(argv=None) -> App:
    parser = App.build_argparser()
    parser.add_argument(
        "--config-file",
        help="Optional JSON file to load before applying CLI overrides",
    )
    args = parser.parse_args(argv)

    config_path = getattr(args, "config_file", None)
    if hasattr(args, "config_file"):
        delattr(args, "config_file")

    cfg = App()
    if config_path:
        cfg = App.load(config_path)

    cfg.apply_cli_overrides(args)
    cfg.validate()
    return cfg


if __name__ == "__main__":
    config = build_config()
    print("Effective configuration (after CLI + config file overrides):")
    config.dump()
