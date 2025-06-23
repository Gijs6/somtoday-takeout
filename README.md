# Somtoday Takeout

A quick and dirty script to save your grades from Somtoday.

Whether you're about to leave school or just want a local backup, this script grabs your grades and saves them as JSON files. Simple as that. (Simple is quite an understatement, but it works, and it allows you to just do whatever you want with the grades.)

## Usage

Install requirements with `pip install -r requirements.txt`.

Run with `python takeout.py <bearer_token> --output <output_dir>`. Just figure out how to get your token, I don't know it anymore.

If you don't specify `--output`, it will save everything to `takeout_result/`.
