import os
import sys
import pandas as pd
from pandas import DataFrame
from pathlib import Path
from .participant import Participants
import git
# import precice


class Results:
    path: Path
    dataFrame: DataFrame

    def __init__(self, path: Path):
        if path.is_file():
            raise IOError(f"File {path} already exists. Aborting.")
        
        self.path = path
        self.dataFrame = DataFrame()

    def append(self, experiment_summary):
        self.dataFrame = pd.concat([self.dataFrame, DataFrame(experiment_summary, index=[0])], ignore_index=True)

    def output_preliminary(self):
        print(f"Write preliminary output to {self.path}")
        self.dataFrame.to_csv(self.path)

        print('-' * os.get_terminal_size().columns)
        print(self.dataFrame)
        print('-' * os.get_terminal_size().columns)
        
    def output_final(self, participants: Participants, args):
        self.dataFrame = self.dataFrame.set_index([f"time step size {p.name}" for p in participants.values()])
        print(f"Write final output to {self.path}")

        git_info = {}

        for participant in participants.values():
            repo = git.Repo(participant.root, search_parent_directories=True)
            chash = str(repo.head.commit)[:7]
            if repo.is_dirty():
                chash += "-dirty"

            git_info[participant.name] = {
                "repo": repo.remotes.origin.url,
                "chash": chash
            }

        metadata = {
            "participants version": git_info,
            "participants": participants,
            # "precice.get_version_information()": precice.get_version_information(),
            # "precice.__version__": precice.__version__,
            "run cmd": "python3 " + " ".join(sys.argv),
            "args": args,
            # "precice_config_params": precice_config_params,
        }

        self.path.unlink()

        with open(self.path, 'a') as f:
            for key, value in metadata.items():
                f.write(f"# {key}:{value}\n")
            self.dataFrame.to_csv(f)

        print('-' * os.get_terminal_size().columns)
        for key, value in metadata.items():
            print(f"{key}:{value}")
        print()
        print(self.dataFrame)
        print('-' * os.get_terminal_size().columns)