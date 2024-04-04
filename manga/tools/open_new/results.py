from dataclasses import astuple
from time import sleep
import subprocess

from tqdm import tqdm

from .tested import Tested


def handle_results(urls: set[str], tested: Tested) -> None:
    """
    Print out the test results and open each of the given URLs that should not be ignored
    """
    if len(tested.unknown) > 0:
        print("The following domains were not known:")
        print("\t" + "\n\t".join(sorted(tested.unknown)))
    if len(tested.failed) > 0:
        print("The following domains could not be opened:")
        print("\t" + "\n\t".join(sorted(tested.failed)))
    if len(tested.skip) > 0:
        print("The following domains were skipped:")
        print("\t" + "\n\t".join(sorted(tested.skip)))
    all_tested = set().union(*astuple(tested))
    if len(all_tested) != len(urls):
        print("The following domains were not tested:")
        print("\t" + "\n\t".join(sorted(urls - all_tested)))
        print("Assuming all remaining URLs must be opened...")
    print("Opening manga...")
    for url in tqdm(urls - tested.ignore - tested.skip, dynamic_ncols=True):
        subprocess.check_call(["open", url], stdout=subprocess.DEVNULL)
        sleep(0.2)  # Rate limit
