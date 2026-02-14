import argparse
import asyncio
import sys
from temporalio.client import Client


async def provision_infra(args):
    """Trigger the core infrastructure workflow."""
    print(
        f"Triggering core infrastructure provisioning for {args.vpc_cidr} in {args.region}..."
    )

    temporal_host = args.temporal_host
    try:
        client = await Client.connect(temporal_host)
        # In a real CLI, we would import the workflow type and start it
        # handle = await client.start_workflow(
        #     "CoreInfraWorkflow",
        #     CoreInfraRequest(vpc_cidr=args.vpc_cidr, region=args.region),
        #     id=f"core-infra-{args.vpc_cidr}",
        #     task_queue="ehub-core-infra",
        # )
        # print(f"Workflow started. ID: {handle.id}")
        print("Mock: Workflow triggered successfully.")
    except Exception as e:
        print(f"Error connecting to Temporal: {e}", file=sys.stderr)
        sys.exit(1)


def cli_parser():
    parser = argparse.ArgumentParser(
        description="eHub CLI - Engineering Hub Management Tool"
    )
    parser.add_argument(
        "--temporal-host", default="localhost:7233", help="Temporal server address"
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Infra command
    infra_parser = subparsers.add_parser("infra", help="Infrastructure management")
    infra_subparsers = infra_parser.add_subparsers(
        dest="subcommand", help="Infra subcommands"
    )

    # Infra provision
    provision_parser = infra_subparsers.add_parser(
        "provision", help="Provision core infrastructure"
    )
    provision_parser.add_argument("--vpc-cidr", required=True, help="VPC CIDR block")
    provision_parser.add_argument("--region", default="us-east-1", help="AWS region")

    return parser


def main():
    cli = cli_parser()
    args = cli.parse_args()

    if args.command == "infra" and args.subcommand == "provision":
        asyncio.run(provision_infra(args))
    else:
        cli.print_help()


if __name__ == "__main__":
    main()
