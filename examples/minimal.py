from dataclasses import dataclass
from options import Options, option


@dataclass
class Train(Options):
    epochs: int = option(default=10, min=1, label="Epoch Count")
    lr: float = option(default=0.01, min=0)


@dataclass
class Main(Options):
    train: Train = Train()
    model: str = option(default="resnet", choices=["resnet", "vit"])


if __name__ == "__main__":
    cfg = Main()
    cfg.dump()

    parser = Main.build_argparser()
    args = parser.parse_args()
    cfg.apply_cli_overrides(args)

    cfg.validate()
    cfg.dump()
