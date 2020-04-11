import subprocess


def get_globus_connection_error(origin):
    try:
        subprocess.run(
            ['globus', 'whoami'], check=True,
            stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return 'Run "globus login"'

    try:
        subprocess.run(
            ['globus', 'ls', origin], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.stdout.decode('utf-8')

    return None
