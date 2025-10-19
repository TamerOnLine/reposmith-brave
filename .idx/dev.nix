# To learn more about how to use Nix to configure your environment,
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find available packages.
  packages = [
    # Essential tools
    pkgs.git
    pkgs.which
    pkgs.ripgrep
    pkgs.fd
    pkgs.nixpkgs-fmt

    # Python environment + uv package manager
    pkgs.python312
    pkgs.uv

    # Enable Node.js support if needed
    # pkgs.nodejs_20
    # pkgs.nodePackages.nodemon

    # Enable Go support if needed
    # pkgs.go

    # Python: pytest (optional)
    pkgs.python312Packages.pytest
  ];

  # Environment variables available in the workspace
  env = {
    # Example: disable venv auto-creation if you rely on uv
    # PIP_REQUIRE_VIRTUALENV = "false";
  };

  idx = {
    # Add VS Code extensions (use publisher.id from https://open-vsx.org/)
    extensions = [
      # "vscodevim.vim"
      # "ms-python.python"
      # "charliermarsh.ruff"  # Ruff linter for Python
    ];

    # Enable IDX previews
    previews = {
      enable = true;
      previews = {
        # Example: run a web server and show it in the IDX web preview
        # web = {
        #   command = ["uv" "run" "python" "app.py"];
        #   manager = "web";
        #   env = { PORT = "$PORT"; };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs once when the workspace is first created
      onCreate = {
        # Example: initialize Python dependencies
        # uv-sync = "uv sync --dev";
      };
      # Runs every time the workspace starts or restarts
      onStart = {
        # Example: run tests or background watchers
        # tests = "uv run pytest -q || true";
      };
    };
  };
}
