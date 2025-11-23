# Github Backup Python script utility

## Setup

Setup `.env` variables to access your github account through the API:

- Rename the `.env.change` file to `.env`
- Change the `GIT_TOKEN_CLASSIC` to your git token

Create your own access token [here](https://github.com/settings/tokens).

Create a virtual environment

```shell
python -m venv ./venv
```

Activate the virtual environment

```shell
#  on Windows
.venv\Scripts\activate

# on macOS and Linux
source .venv/bin/activate
```

Install Dependencies

```shell
pip install -r requirements.txt
```

## Usage

Activate the virtual environment

```shell
#  on Windows
.venv\Scripts\activate

# on macOS and Linux
source .venv/bin/activate
```

Run `backup.py` file

```py
python3 backup.py
```
