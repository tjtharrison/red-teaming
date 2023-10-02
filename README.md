# kubernetes-red-teaming

This project contains handy scripts for using the Datadog project [stratus-read-team](https://stratus-red-team.cloud/) to perform red teaming activities on a kubernetes cluster.

## Preparation

You will need to have your `~/.kube/config` file configured to point to the cluster you want to test. This file will be mounted onto the container when it is run.

You will also need a functioning docker installation on your machine.

## Installation

There are no installation steps required for this project.

## Usage

To run the tool, simply run the following command:

```bash
python3 readteam.py
```

You will be presented with a menu of options to choose from. The options are fairly self explanatory and match up 
with the functionality described in the [stratus-read-team](https://stratus-red-team.cloud/) project.
