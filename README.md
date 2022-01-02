# Moodle downloader

### Setup
1. Install [Python](https://www.python.org/) >=3.8 
2. Verify that `python --version` shows a version equal to or higher then 3.8
    Otherwise use [pyenv](https://github.com/pyenv/pyenv#installation) to install version 3.8
3. `pip3 install -r requirements.txt`
4. run `python3 downloader.py -u USERNAME -p PASSWORD -y YEAR`

### Configuration

#### Flags

* **-u**, **--username**: Moodle username
* **-p**, **--password**: Moodle password
* **-y**, **--year**: Moodle school year (`2018-19` or `2019-20` or `2020-21`)

### Output example:
![output](https://user-images.githubusercontent.com/35016381/130121235-4d757aaf-2f53-4dcd-8deb-18b8ceaa9feb.PNG)

### Notes
* All files will be saved at the user's Documents folder and organized by year and course name

* Only tested for IPLeiria's moodle page 

### License

<a href="" target="_blank">MIT</a> - <b>Copyright © 2021 • Pedro Santos</b>
