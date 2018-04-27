# When you see something you like and would like to use it, open an issue about
# abstracting it out into a reusable package, possibly installable via Package
# Control.

import re
import webbrowser

import sublime_plugin


def _extract_github_url(view):
    line = view.line(view.sel()[0].b)
    line = view.substr(line)

    # Format: <githubdomain>/x/y, <githubdomain>/x/y/issues/#<number>

    match = re.match(
        '^.*'
        '(?P<url>https:\\/\\/github\\.com'
        '\\/[a-zA-Z0-9_-]+\\/[a-zA-Z0-9_-]+'
        '(?:\\/issues\\/[0-9]+)?'
        ')',
        line
    )

    if match:
        return match.group('url')

    # Format: x/y, x/y#<number>

    match = re.findall(
        '[a-zA-Z0-9_-]+\\/[a-zA-Z0-9_-]+(?:#[0-9]+)?',
        line
    )

    if match:
        return 'https://github.com/' + match[0].replace('#', '/issues/')

    match = re.findall('#[0-9]+', line)
    if match:
        # TODO remove hardcoded package name.
        return 'https://github.com/' + match[0].replace('#', 'NeoVintageous/NeoVintageous/issues/')


class GitFormatGithubUrlCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        line = self.view.line(self.view.sel()[0].b)

        # Try convert https://github.com/x/y/issues/42 to trackback x/y#42.
        url_region = self.view.find(
            'https:\\/\\/github.com'
            '\\/[a-zA-Z0-9_-]+'
            '\\/[a-zA-Z0-9_-]+'
            '\\/issues\\/[0-9]+',
            line.begin())

        if url_region:
            url = self.view.substr(url_region)
            url = url.replace('https://github.com/', '')
            url = url.replace('/issues/', '#')

            self.view.replace(edit, url_region, url)
        else:
            # Try convert x/y#42 -> GitHub url.

            url_region = self.view.find(
                '[a-zA-Z0-9_-]+'
                '\\/[a-zA-Z0-9_-]+'
                '#[0-9]+',
                line.begin())

            if url_region:
                url = self.view.substr(url_region)
                url = 'https://github.com/' + url
                url = url.replace('#', '/issues/')

                self.view.replace(edit, url_region, url)


class GitOpenCommand(sublime_plugin.TextCommand):

    def run(self, edit, event=None):
        url = _extract_github_url(self.view)
        if url:
            webbrowser.open_new_tab(url)