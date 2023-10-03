"""Wrapper script for the stratus-red-team project to simplify usage."""

import os
import subprocess
import sys

import inquirer


def get_available_platforms():
    """
    Get the available platforms.

    Returns:
        list: The list of available platforms
    """
    available_platforms = []

    list_output = (
        subprocess.check_output(build_base_command() + " list", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    for line in list_output:
        if "." in line:
            available_platforms.append(line.split(" ")[1].split(".")[0].lower())

    # Remove duplicates from list
    available_platforms = list(dict.fromkeys(available_platforms))

    # Remove spurious entries
    available_platforms.remove("the")

    return available_platforms


def get_platform():
    """
    Get the platform to run on.

    Raises:
        KeyboardInterrupt: If the user exits the program

    Returns:
        str: The platform to run on
    """
    try:
        questions = [
            inquirer.List(
                "platform",
                message="What platform would you like to run on?",
                choices=[
                    "aws",
                    "k8s",
                ],  # This should be replaced with get_available_platforms() once flags are found.
            ),
        ]
        answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)

    except KeyboardInterrupt as error_message:
        raise KeyboardInterrupt from error_message

    return answers["platform"]


def build_base_command(platform=""):
    """
    Build the base command to run.

    Args:
        platform (str, optional): The platform to run on. Defaults to "".

    Returns:
        str: The base command to run
    """

    if platform == "k8s":
        additional_flags = "-v /Users/tim/.kube/:/root/.kube/ "
    elif platform == "aws":
        additional_flags = "-e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN -e AWS_DEFAULT_REGION "
    else:
        additional_flags = ""

    base_command = "".join(
        "docker run --rm -v "
        "/Users/tim/.stratus-red-team/:/root/.stratus-red-team/ "
        f"{additional_flags}"
        "ghcr.io/datadog/stratus-red-team"
    )

    return base_command


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


def list_attacks(platform=""):
    """
    List the attack types available.

    Args:
        platform (str): The platform to run on

    Returns:
        list: The list of attack types
    """
    attack_list = []

    list_output = (
        subprocess.check_output(build_base_command() + " list", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    for line in list_output:
        if platform in line:
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
        subprocess.check_output(build_base_command() + " status", shell=True)
        .decode("utf-8")
        .split("\n")
    )

    for line in list_output:
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
        subprocess.check_output(build_base_command() + " status", shell=True)
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
    subprocess.call(build_base_command() + f" cleanup {attack_id}", shell=True)


def main():
    """Run the main function."""

    try:
        command = get_command()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

    if command == "list":
        try:
            platform = get_platform()
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)

        attack_list = list_attacks(platform)
        print("\nAvailable attacks:")
        for attack in attack_list:
            print(attack)
    elif command == "detonate":
        try:
            platform = get_platform()
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)

        attack_list = list_attacks(platform)
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
        subprocess.call(
            build_base_command(platform) + f" detonate {attack}", shell=True
        )
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
        subprocess.call(build_base_command() + f" cleanup {attack}", shell=True)

    elif command == "cleanup all":
        print("\nCleaning up all attacks")

        detonated_list = list_detonated()

        if len(detonated_list) == 0:
            print("\nNo attacks to cleanup")
            sys.exit(0)

        for attack in detonated_list:
            print(f"Cleaning up attack: {attack}")
            subprocess.call(build_base_command() + f" cleanup {attack}", shell=True)


if __name__ == "__main__":
    main()
