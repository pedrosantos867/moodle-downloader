import requests, os, re, argparse, textwrap
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''
                        +-----------------------------------------------------------------+
                        |      Python tool to download course resources from Moodle       |
                        |        Only works for IPLeiria Moodle (ead.ipleiria.pt)         |
                        |                      Made by Pedro Santos                       |
                        +-----------------------------------------------------------------+''')
                                     , usage='python downloader.py -u xxxxxxx -p password -y xxxx-xx')
    parser.add_argument('-u', '--username', help='username of moodle')
    parser.add_argument('-p', '--password', help='password of moodle')
    parser.add_argument('-y',  '--year', choices=['2018-19', '2019-20', '2020-21'], help='school year')
    args = parser.parse_args()

    if args.username and args.password and args.year:
        print("username: " + args.username + " password: " + args.password + " year: " + args.year)
    else:
        print('Wrong credentials.\nUsage: python downloader.py -u xxxxxxx -p password -y xxxx-xx')
        return

    BASE_URL = 'https://ead.ipleiria.pt/' + str(args.year)
    SAVE_LOCATION = os.path.expanduser('~/Documents/moodle-dowloader-ipleiria/' + str(args.year))

    r = requests.get(BASE_URL + '/login/index.php')
    cookie = r.cookies.get_dict()
    pattern = '<input type="hidden" name="logintoken" value="\w{32}">'
    token = re.findall(pattern, r.text)
    token = re.findall("\w{32}", token[0])
    payload = {'username': args.username, 'password': args.password, 'anchor': '', 'logintoken': token[0]}
    session = requests.Session()
    r = session.post(BASE_URL + '/login/index.php', cookies=cookie, data=payload)

    if not session.cookies:
        print("[INFO]       Wrong credentials.")
        return
    else:
        print("[INFO]       Logged in with success!")
        print("[INFO]       Saving to: " + SAVE_LOCATION)

    html_content = r.text
    soup = BeautifulSoup(html_content, 'html.parser')

    all_links = soup.find_all('a')

    courses_id_name = dict()
    courses = []
    for l in all_links:
        if args.year == '2018-19':
            if 'href' not in l.attrs:
                continue
            if BASE_URL + '/course/view.php?id=' in l.attrs[
                'href'] and 'target' not in l.attrs and 'tabindex' not in l.attrs:
                courses.append(l)
        elif args.year == '2020-21':
            if BASE_URL + '/course/view.php?id=' in l.attrs['href'] and 'title' in l.attrs:
                courses.append(l)
        else:
            if BASE_URL + '/course/view.php?id=' in l.attrs['href'] and 'target' not in l.attrs and 'tabindex' not in l.attrs:
                courses.append(l)

    for c in courses:
        query = urlparse(c.attrs['href']).query
        params = parse_qs(query)
        # Add course to dict id -> name
        if args.year == '2020-21':
            courses_id_name[params['id'][0]] = c.attrs['title']
        else:
            courses_id_name[params['id'][0]] = c.text

    # Create base folder
    if (os.path.isdir(SAVE_LOCATION) == False):
        os.makedirs(SAVE_LOCATION)

    # Iterate over all courses
    for id in courses_id_name:
        print("[COURSE]     " + courses_id_name[id])

        # Create course folder
        if (os.path.isdir(SAVE_LOCATION + '\\' + courses_id_name[id]) == False):
            os.mkdir(SAVE_LOCATION + '\\' + courses_id_name[id])

        # Get all links from a certain course
        r = session.get(BASE_URL + '/course/resources.php?id=' + id)
        r.text

        html_content = r.text
        soup = BeautifulSoup(html_content, 'html.parser')

        all_links = soup.find_all('a')

        for l in all_links:
            char_to_replace = {'/': '-',
                               '|': '-',
                               ':': '-',
                               '\"': '',
                               '*': ''}

            # If finds a link to a folder (repeated code)
            if BASE_URL + '/mod/folder/' in l.attrs['href']:  # If is a folder
                if (os.path.isdir(SAVE_LOCATION + '\\' + courses_id_name[id] + '\\' + l.text) == False):
                    os.path.isdir(SAVE_LOCATION + '\\' + courses_id_name[id] + '\\' + l.text)

                    r = session.get(l.attrs['href'])
                    r.text

                    html_content = r.text
                    soup = BeautifulSoup(html_content, 'html.parser')

                    all_links = soup.find_all('a')

                    for l in all_links:
                        if 'mod_folder/content/' in l.attrs['href']:
                            r = session.get(l.attrs['href'], stream=True)

                            filepath = SAVE_LOCATION + '\\' + courses_id_name[id].strip() + '\\' + (l.text).translate(
                                str.maketrans(char_to_replace)).strip()
                            print('[DOWNLOADED] ' + (l.text).translate(str.maketrans(char_to_replace)).strip())

                            with open(filepath, 'wb') as f:
                                f.write(r.content)

            if BASE_URL + '/mod/resource/' in l.attrs['href']:
                r = session.get(l.attrs['href'], stream=True)
                filename = (l.text).translate(str.maketrans(char_to_replace)).strip() + '.pdf'
                if (r.headers['Content-Type'] == 'application/pdf'):
                    if '.pdf' not in filename:
                        filename += '.pdf'
                elif r.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    filename += '.docx'
                elif r.headers['Content-Type'] == 'application/zip':
                    filename += '.zip'
                elif r.headers['Content-Type'] == 'application/x-rar-compressed':
                    filename += '.rar'
                elif r.headers['Content-Type'] == 'application/x-7z-compressed':
                    filename += '.7zip'
                elif r.headers['Content-Type'] == 'text/plain; charset=utf-8':
                    filename += '.txt'
                elif r.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    filename += '.xlsx'
                elif r.headers['Content-Type'] == 'application/epub+zip':
                    filename += '.epub'
                elif r.headers['Content-Type'] == 'image/gif':
                    filename += '.gif'

                with open(SAVE_LOCATION + '\\' + courses_id_name[id].strip() + '\\' + filename, 'wb') as f:
                    f.write(r.content)
                    print('[DOWNLOADED] ' + filename)
    print("[INFO]       All file have been downloaded!")
    print("[INFO]       Saved to: " + SAVE_LOCATION)
if __name__ == '__main__':
    main()
