import jenkins
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, type=str)
    parser.add_argument('--user', required=True, type=str)
    parser.add_argument('--pwd', required=True, type=str)
    parser.add_argument('--colors', required=True, type=str)
    args = parser.parse_args()
    server = jenkins.Jenkins(args.host, username=args.user, password=args.pwd)
    colors = args.colors.split(',')
    for job in server.get_jobs():
        job_color = job['color']
        if job_color in colors:
            print("{0} is currently {1}".format(job['name'], job_color))

if __name__ == '__main__':
    main()
