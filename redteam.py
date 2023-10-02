"""Wrapper script for the stratus-red-team project to simplify usage."""

import os
import subprocess
import sys

import inquirer

BASE_COMMAND = "".join(
    "docker run --rm -v "
    "/Users/tim/.stratus-red-team/:/root/.stratus-red-team/ "
    f"-v {os.path.expanduser( '~' )}/.kube/config:/root/.kube/config "
    "ghcr.io/datadog/stratus-red-team"
)


def get_command():
    """
    Get the command to run.

    Raises:
        KeyboardInterrupt: If the user exits the program

    Returns:
        str: The command to run
    """
    try:
        questions = [
            inquirer.List(
                "command",
                message="What would you like to do?",
                choices=["list", "detonate", "status", "cleanup", "cleanup all"],
            ),
        ]
        answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

    except KeyboardInterrupt as error_message:
        raise KeyboardInterrupt from error_message

    return answers["command"]


def list_attacks():
    """
    List the attack types available.

    Returns:
        list: The list of attack types
    """
    attack_list = []

    list_output = (
        subprocess.check_output(BASE_COMMAND + " list", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    for line in list_output:
        if "k8s" in line:
            attack_list.append(line.split(" ")[1])

    return attack_list


def get_status():
    """
    Get the status of the attacks.

    Returns:
        list: The list of attacks and their status
    """
    status_list = []

    list_output = (
        subprocess.check_output(BASE_COMMAND + " status", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    for line in list_output:
        if "k8s" in line or "STATUS" in line or "+--" in line:
            status_list.append(line)

    return status_list


def list_detonated():
    """
    List the attacks that have been detonated.

    Returns:
        list: The list of attacks that have been detonated
    """
    detonated_list = []

    list_output = (
        subprocess.check_output(BASE_COMMAND + " status", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    for line in list_output:
        if "DETONATED" in line:
            detonated_list.append(line.split(" ")[1])

    return detonated_list


def do_cleanup(attack_id):
    """
    Cleanup the attack.

    Args:
        attack_id (str): The attack ID to clean up
    """
    subprocess.call(BASE_COMMAND + f" cleanup {attack_id}", shell=True)


def main():
    """Run the main function."""
    try:
        command = get_command()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

    if command == "list":
        attack_list = list_attacks()
        print("\nAvailable attacks:")
        for attack in attack_list:
            print(attack)
    elif command == "detonate":
        attack_list = list_attacks()
        questions = [
            inquirer.List(
                "attack",
                message="Which attack would you like to run?",
                choices=attack_list,
            ),
        ]
        answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

        attack = answers["attack"]

        print(f"\nRunning attack: {attack}")
        subprocess.call(BASE_COMMAND + f" detonate {attack}", shell=True)
    elif command == "status":
        status_list = get_status()
        print("\nAttack status:")
        for status in status_list:
            print(status)
    elif command == "cleanup":
        detonated_list = list_detonated()

        if len(detonated_list) == 0:
            print("\nNo attacks to cleanup")
            sys.exit(0)

        questions = [
            inquirer.List(
                "attack",
                message="Which attack would you like to cleanup?",
                choices=detonated_list,
            ),
        ]
        answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

        attack = answers["attack"]

        print(f"\nCleaning up attack: {attack}")
        subprocess.call(BASE_COMMAND + f" cleanup {attack}", shell=True)

    elif command == "cleanup all":
        print("\nCleaning up all attacks")

        detonated_list = list_detonated()

        if len(detonated_list) == 0:
            print("\nNo attacks to cleanup")
            sys.exit(0)

        for attack in detonated_list:
            print(f"Cleaning up attack: {attack}")
            subprocess.call(BASE_COMMAND + f" cleanup {attack}", shell=True)


if __name__ == "__main__":
    main()
