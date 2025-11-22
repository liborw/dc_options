from dataclasses import dataclass
from dc_options import Options, option, render_options


@dataclass
class Logging(Options):
    level: str = option(
        default="info",
        choices=["debug", "info", "warning", "error"],
        description="Verbosity of the training logs",
    )
    directory: str = option(
        default="runs/",
        description="Destination folder for checkpoints and metrics",
    )
    flush_interval: int = option(
        default=10,
        min=1,
        description="How often (in steps) metrics are synced to disk",
    )


@dataclass
class Train(Options):
    epochs: int = option(default=10, min=1, label="Epoch Count")
    lr: float = option(default=0.01, min=0, description="Learning rate")
    batch_size: int = option(default=32, min=1, description="Samples per optimizer step")
    logging: Logging = option(default_factory=Logging)


if __name__ == "__main__":
    cfg = Train()
    print("== Default configuration ==")
    print(render_options(cfg))

    cfg.set("logging.level", "debug")
    cfg.set("epochs", 5)

    cfg.validate()
    print("\n== After overrides ==")
    print(render_options(cfg))
    print(f"Logs directory via path lookup: {cfg.get('logging.directory')}")
